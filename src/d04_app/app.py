import numpy as np
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import CsrfProtect
from flask_sqlalchemy import SQLAlchemy
import plotly.express as px
import pandas as pd
import json
from d00_utils.load_confs import load_parameters
from d01_data_processing.data_cleaning import clean_all_data
from d01_data_processing.spotify_user import SpotifyUser    
from d03_database_interaction.db_operations import insert_new_user_to_database, remove_user_from_database, select_from_table
import d04_app.forms as forms
import d04_app.startup as startup
# we need to add the following to requirements.txt: passlib, plotly, json
csrf = CsrfProtect()
params = load_parameters()

app = Flask(__name__)
app.secret_key = params['secret_key']
app.config.from_object('d04_app.config')
csrf.init_app(app)
db = SQLAlchemy(app, session_options={'autocommit': False})


@app.route('/')
def home():
	'''
	The home page introduces the user to the app. The user can login if currently
	logged out or log out if currently logged in. The user can go to the welcome page
	by clicking the meet the team button. The user can also view their music data
	if they are currently logged in.
	'''
	if session.get('loggedin', False) is True: # if logged in, display a button for logout
		login_text = "Logout"
	if session.get('loggedin', False) is False: # if not logged in, display a button for login
		login_text = "Login"

	return render_template('home.html', login_text = login_text)


@app.route('/welcome')
def welcome():
	'''
	The welcome page displays information about the app and the developers.
	'''
	return render_template('welcome.html')


@app.route('/newlogin', methods=['GET', 'POST'])
def newlogin():
	'''
	This page allows a user to sign up to Spotify Share. The user must enter
	a username and password. If the username matches a username of a listener
	in the database, then the page redirects to itself and indicates that the
	username is already taken. If the username is not currently taken by another
	userin the database, then this page redirects to a Spotify page where the user
	can give Spotify Share authorization to access their Spotify data. The user
	is then redirected to callback on our website which redirects them to home
	after inserting their data into the database.

	The user can also return to the home page from here by clicking the back button.
	'''
	form = forms.NewLoginForm() # have login form return username

	# check if exists already, if not, then go to spotify login
	if form.validate_on_submit():
		new_username = form.username.data
		hashed_password = pbkdf2_sha256.hash(form.password.data, rounds = 20000)

		username_list = np.array(select_from_table("""
							SELECT l.username
							FROM Listeners l""", db_engine=db.engine))

		if new_username in username_list:   # return to page with error if the username is already registered
			flash('Username is already registered, try another username.')
			return redirect('/newlogin')

		session.permanent = True
		session["current_username"] = new_username
		session['hashed_password'] = hashed_password

		response = startup.getUser()
		return redirect(response) # user is redirected from Spotify back to /callback

	return render_template('newlogin.html', form=form)


@app.route('/loginOrLogout', methods=['GET', 'POST'])
def loginOrLogout():
	'''
	If the user is not logged in, it redirects to the returning login page. If the
	user is logged in, it logs the user out by clearing the username and password
	and setting loggedin to False.
	'''
	loggedin = session.get('loggedin', False)

	if loggedin is False:
		return returninglogin()

	if loggedin is True:
		session["loggedin"] = False
		session["current_username"] = ""
		session['hashed_password'] = ""
		return home()


@app.route('/returninglogin', methods=['GET', 'POST'])
def returninglogin():
	'''
	This page allows users to login if they have previously signed up to our app.
	It first prompts the user for a username and password and checks if the username
	and password pair matches a pair in the database. If it finds a match, it
	refreshes the account if it has been more than 3 days since last time account was
	refreshed. Then it indicates that the user is logged in by changing the loggedin
	and current_user attributes of session and redirects to the home page.

	The user can also return to the home page or continue to the sign up page
	for new users.
	'''
	form = forms.ReturningLoginForm() # have returning login form return username and password
	# check if exists already, if not, then
	if form.validate_on_submit():

		new_username, new_password = form.username.data, form.password.data

		listener_list = np.array(select_from_table("""
							SELECT l.username, l.password, l.refresh_token, l.creation_datetime
							FROM Listeners l
							WHERE l.username = '%s' """ % new_username, db_engine=db.engine))

		# if no listener in Listeners has the same username as new_username
		if ((listener_list.size and listener_list.ndim) == 0):
			flash('Username is not registered. If you are a new user, please go to the newlogin page to sign up.')
			return redirect('/returninglogin')

		# check if passed password matches the hashed password stored in the database
		db_password, db_refresh_token = listener_list[0][1], listener_list[0][2]
		if not pbkdf2_sha256.verify(new_password, db_password):
			flash('Password is incorrect. Try again.')
			return redirect('/returninglogin')

		session.permanent = True
		session["current_username"] = new_username

		# check if it has been more than x days since last acct update time
		# if so, use refresh token to request new auth code
		acct_update_time = listener_list[0][3].to_pydatetime()
		time_delta = datetime.utcnow() - acct_update_time
		if time_delta > timedelta(days=params['acct_refresh_time']): # refresh database data, need to save hashed_password in session for use in callback
			session['hashed_password'] = pbkdf2_sha256.hash(new_password, rounds = 20000)
			return redirect(f'/callback/?reauth_code={db_refresh_token}')
		else: # log in the user, don't need to store the password in session
			session["loggedin"] = True
			return redirect('/yourdata')

	return render_template('returninglogin.html', form=form)


@app.route('/callback')
def callback():
	"""
	This code gets the access token and returns to auth the access token that was
	previously stored in .cache thing. access token and refresh token
	are written to the database, along with all the other information we
	pull from the spotify api

	If refresh_token is an empty string, treat as new user. Else, treat as a returning user and
	perform reauthentication.
	"""
	# first-time auth token
	user_auth_code, user_reauth_code = request.args.get('code', None), request.args.get('reauth_code', None)

	# current username and password
	current_username = session.get('current_username', None)
	hashed_password = session.get('hashed_password', None)

	# exchange user_auth_code for access token, refresh token
	if user_auth_code is not None:
		user_token_data = startup.getUserToken(code=user_auth_code)

	# refresh auth info
	elif user_reauth_code is not None:
		user_token_data = startup.refreshToken(refresh_token=user_reauth_code)
		remove_user_from_database(username=current_username,
								  db_engine=db.engine)
	# insert new user to database
	new_user = SpotifyUser(username=current_username,
						   from_scratch=False,
						   token=user_token_data[0])

	new_user_data = clean_all_data(new_user=new_user,
								   new_password=hashed_password,
								   user_token_data=user_token_data)

	insert_new_user_to_database(new_user_data=new_user_data,
								db_engine=db.engine)

	session["loggedin"] = True # only count the user as logged in if inserting the data into the database is successful
	session['hashed_password'] = "" # remove the hashed_password from session

	return redirect('/')


@app.route('/yourdata', methods=['GET', 'POST'])
def yourdata():
	'''
	This page redirects to the artist page if the user is logged in and otherwise
	redirects to the returning login page for the user to login in.
	'''
	loggedin = session.get('loggedin', False)

	if loggedin is False:
		return returninglogin()
	if loggedin is True:
		return artistpage()


@app.route('/artistpage', methods=['GET', 'POST'])
def artistpage():
	# This page displays top artist and top track information for a user who
	# is logged in. It also allows the user to return to the home page.
    current_username = session.get('current_username', None)
    df = pd.DataFrame(dict(
        r=[1, 5, 2, 2, 3],
        theta=['processing cost','mechanical properties','chemical stability','thermal stability', 'device integration']))
    fig = px.line_polar(df, r='r', theta='theta', line_close=True)
    fig.update_traces(fill='toself')
    fig1 = fig
    results = np.array(select_from_table("""
	SELECT a.artist_image_url, a.artist_name
	FROM Topartists t, Listeners l, Artists a
	WHERE a.artist_id = t.artist_id 
		and l.listener_id = t.listener_id 
		and l.username = '%s'""" % current_username,
							db_engine=db.engine))
    query2 = np.array(
		select_from_table("""
	SELECT distinct t.track_name, a.artist_name
	FROM TopTracks tt, Tracks t, Listeners l, Artists a, CreatedBy c, AlbumContainsTrack act, Albums al
	WHERE act.album_id = al.album_id 
		and act.track_id = t.track_id 
		and c.artist_id = a.artist_id 
		and tt.track_id = c.track_id 
		and c.track_id = t.track_id
		and l.listener_id = tt.listener_id 
		and l.username = '%s'""" % current_username,
							db_engine=db.engine))
    query3 = np.array(
	select_from_table("""
	SELECT l.listener_image_url, l.display_name
	FROM Listeners l
	WHERE l.username = '%s'""" % current_username, db_engine=db.engine))
    return render_template('listener_artists.html',
							listener_name=current_username,
							data=results,
							query2=query2,
							query3=query3,
                            fig1=fig1)


if __name__ == '__main__':
	# app.run(host='vcm@vcm-12647.vm.duke.edu', port=443, debug=params['debug_mode_on'])
    app.run(host='0.0.0.0', port=params['port'], debug=params['debug_mode_on'])
