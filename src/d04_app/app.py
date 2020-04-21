import numpy as np
from datetime import datetime, timedelta
from passlib.hash import pbkdf2_sha256
from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_wtf import CsrfProtect
from flask_sqlalchemy import SQLAlchemy

from d00_utils.load_confs import load_parameters
from d01_data_processing.data_cleaning import clean_all_data
from d01_data_processing.spotify_user import SpotifyUser    
from d03_database_interaction.db_operations import insert_new_user_to_database, remove_user_from_database, select_from_table
import d04_app.forms as forms
import d04_app.startup as startup

csrf = CsrfProtect()
params = load_parameters()

app = Flask(__name__)
app.secret_key = params['secret_key']
app.config.from_object('d04_app.config')
csrf.init_app(app)
db = SQLAlchemy(app, session_options={'autocommit': False})


loggedin = False
username = ""


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/welcome')
def welcome():
    return render_template('welcome.html')


@app.route('/newlogin', methods=['GET', 'POST'])
def newlogin():
    form = forms.NewLoginForm() # have login form return username
    # check if exists already, if not, then go to spotify login
    if form.validate_on_submit():

        new_username = form.username.data
        # hash the password before proceeding
        new_password = pbkdf2_sha256.hash(form.password.data, rounds = 20000)
        session['new_username'] = new_username
        session['new_password'] = new_password

        username_list = np.array(select_from_table("""
                            SELECT l.username
                            FROM Listeners l""", db_engine=db.engine))

        if new_username in username_list:   # return to page with error if the username is already registered
            flash('Username is already registered, try another username.')
            return redirect('/newlogin')

        response = startup.getUser()
        return redirect(response) # user is redirected from Spotify back to /callback

    return render_template('newlogin.html', form=form)


@app.route('/returninglogin', methods=['GET', 'POST'])
def returninglogin():
    '''
    Check if username exists already in database. Refresh account if it has been more
    than 3 days since last time account was refreshed and redirect to the artist page.
    '''
    form = forms.ReturningLoginForm() # have returning login form return username and password
    # check if exists already, if not, then
    if form.validate_on_submit():
        new_username, new_password = form.username.data, form.password.data
        session['new_username'] = new_username

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


        # check if it has been more than x days since last acct update time
        # if so, use refresh token to request new auth code
        acct_update_time = listener_list[0][3].to_pydatetime()
        time_delta = datetime.utcnow() - acct_update_time
        if time_delta > timedelta(days=params['acct_refresh_time']):
            return redirect(f'/callback/?reauth_code={db_refresh_token}')
        else:
            global loggedin;
            global username
            loggedin, username = True, new_username
            return redirect(f'/artistpage/{new_username}')

    return render_template('returninglogin.html', form=form)


@app.route('/callback/')
def callback():
    """
    this code gets the access token and returns to auth the access token that was
    previously stored in .cache thing. access token and refresh token
    are written to the database, along with all the other information we
    pull from the spotify api

    If refresh_token is an empty string, treat as new user. Else, treat as a returning user and
    perform reauthentication.
    """
    # first-time auth token
    user_auth_code, user_reauth_code = request.args.get('code', None), request.args.get('reauth_code', None)
    new_username, new_password = session.get('new_username', None), session.get('new_password', None)
    global loggedin; global username
    loggedin, username = True, new_username

    # exchange user_auth_code for access token, refresh token
    if user_auth_code is not None:
        user_token_data = startup.getUserToken(code=user_auth_code)

    # refresh auth info
    elif user_reauth_code is not None:
        user_token_data = startup.refreshToken(refresh_token=user_reauth_code)
        remove_user_from_database(username=new_username,
                                  db_engine=db.engine)
    # insert new user to database
    new_user = SpotifyUser(username=new_username,
                           from_scratch=False,
                           token=user_token_data[0])

    new_user_data = clean_all_data(new_user=new_user,
                                   new_password=new_password,
                                   user_token_data=user_token_data)

    insert_new_user_to_database(new_user_data=new_user_data,
                                db_engine=db.engine)

    return redirect(f'/artistpage/{new_username}')


@app.route('/yourdata', methods=['GET', 'POST'])
def yourdata():
	if loggedin is False:
		return returninglogin()
	if loggedin is True:
		return artistpage(username)


@app.route('/artistpage/<listener_username>', methods=['GET', 'POST'])
def artistpage(listener_username):
    results = np.array(
        select_from_table("""
    SELECT a.artist_image_url, a.artist_name
    FROM Topartists t, Listeners l, Artists a
    WHERE a.artist_id = t.artist_id 
    and l.listener_id = t.listener_id 
    and l.username = '%s'""" % listener_username,
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
     and l.username = '%s'""" % listener_username,
                            db_engine=db.engine))

    return render_template('listener_artists.html',
                            listener_name=listener_username,
                            data=results,
                            query2=query2)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=params['port'], debug=params['debug_mode_on'])