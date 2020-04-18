from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy

from d00_utils.load_confs import load_parameters
from d01_data_processing.data_cleaning import clean_all_data
from d01_data_processing.spotify_user import SpotifyUser    
import d04_app.forms as forms
import d04_app.startup as startup
from d03_database_interaction.db_operations import insert_new_user_to_database, select_from_table
import d04_app.models
import numpy as np
from flask_wtf import CsrfProtect

csrf = CsrfProtect()
params = load_parameters()

app = Flask(__name__)
app.secret_key = params['secret_key']
app.config.from_object('d04_app.config')
csrf.init_app(app)
db = SQLAlchemy(app, session_options={'autocommit': False})


@app.route('/')
def home():
    return render_template('home.html')
    

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# TODO: need a new user/returning user login page 
# returning user: check if username exists already in database, if so, then refresh creds
# and redirect to homepage -- i.e. do what spotipy does 

# this is the new user method
@app.route('/newlogin', methods=['GET', 'POST'])
def newlogin():
    form = forms.NewLoginForm() # have login form return username
    # check if exists already, if not, then go to spotify login 
    if form.validate_on_submit():
        
        new_username = form.username.data
        new_password = form.password.data
        session['new_username']= new_username

        # TODO: check that desired username is unique by querying database and verifying no matches 
        # response is the redirect url to Spotify permission page
        response = startup.getUser()  
        return redirect(response) # user is redirected from Spotify back to /callback

    return render_template('newlogin.html', form=form)

# this is the returning user method 
@app.route('/returninglogin', methods=['GET', 'POST'])
def returninglogin():
    form = forms.ReturningLoginForm() # have returning login form return username and password
    # check if exists already, if not, then 
    if form.validate_on_submit():
        
        new_username = form.username.data
        new_password = form.password.data
        session['new_username']= new_username

        # if username is in database
        	# if correct password
        usernamecheck=np.array(select_from_table("""
        SELECT l.username,
        FROM  Listeners l,
        WHERE l.username = '%s'""" % new_username, db_engine=db.engine))
       
        if usernamecheck is None:
            response = startup.getUser() 
            return redirect(response)
        else:
            results = np.array(select_from_table("""
            SELECT a.artist_image_url, a.artist_name
            FROM Topartists t, Listeners l, Artists a
            WHERE a.artist_id = t.artist_id and l.listener_id = t.listener_id and l.username = '%s'""" % usernamecheck, db_engine=db.engine))
            return render_template('listener_artists2.html', 
                            listener_name=usernamecheck,
                            data=results)
        	# if incorrect password

        # if username not in the database 

        # response is the redirect url to Spotify permission page
        response = startup.getUser()  
        return redirect(response) # user is redirected from Spotify back to /callback

    return render_template('returninglogin.html', form=form)
    
@app.route('/artistpage/<listener_name>', methods=['GET', 'POST'])
def artistpage(listener_name):
    # results=db.session.query(d04_app.models.Topartists.artist_id).join(d04_app.models.Listeners, d04_app.models.Topartists.listener_id == d04_app.models.Listeners.listener_id).all()
    # results=db.session.query(d04_app.models.Topartists.artist_id, d04_app.models.Topartists.listener_id)
    results = np.array(select_from_table("""
    SELECT a.artist_image_url, a.artist_name
    FROM Topartists t, Listeners l, Artists a
    WHERE a.artist_id = t.artist_id and l.listener_id = t.listener_id and l.display_name = '%s'""" % listener_name, db_engine=db.engine))
    return render_template('listener_artists.html', 
                            listener_name=listener_name,
                            data=results)
@app.route('/callback/')
def callback():
    """
    #this code gets the access token and returns to auth the access token that was 
    #previously stored in .cache thing. access token and refresh token 
    are written to the database, along with all the other information we 
    pull from the spotify api. 
    """
    user_auth_code = request.args['code']
    # exchange user_auth_code for access token, refresh token
    user_token_data = startup.getUserToken(code=user_auth_code)

    #when we change how spotifyUser is initialized. 
    new_user = SpotifyUser(username=session.get("new_username", None), 
                           from_scratch=False, 
                           token=user_token_data[0])

    new_user_data = clean_all_data(new_user=new_user, 
                                   user_token_data=user_token_data)
    # TODO: this step takes a while, perhaps redirect to a 
    # "loading" page? 
    insert_new_user_to_database(new_user_data=new_user_data, 
                                db_engine=db.engine)

    return redirect('/')


@app.route('/database', methods=['GET', 'POST'])
def database():
    listener_names = db.session.query(d04_app.models.Listeners.display_name)
    dropdown_list = []
    for listener in listener_names:
        dropdown_list.append(listener[0])
    form = forms.artistsform.form(dropdown_list) #artistsforms is just the name of the form
    if form.validate_on_submit():
        try:
            return redirect(url_for('/artistpage/'+ form.listener_sel.data)) # not sure if this is right
        except:
            return redirect('/')
    return render_template('database.html', dropdown_list=dropdown_list, form=form)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=params['port'], debug=params['debug_mode_on'])