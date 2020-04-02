from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import d04_app.forms as forms
import d04_app.startup as startup
import d04_app.authentication as authentication
from d04_app.db_operations import insert_new_user_to_database

from d01_data_processing.data_cleaning import clean_all_data
from d01_data_processing.spotify_user import SpotifyUser	
	
app = Flask(__name__)
app.secret_key = 'cs316'
app.config.from_object('d04_app.config')
db = SQLAlchemy(app, session_options={'autocommit': False})

import d04_app.models

@app.route('/')
def home():
    return render_template('home.html')
    

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

# TODO: need a new user/returning user login page 
# returning user: check if username exists already in database, if so, then refresh creds
# and redirect to homepage -- i.e. do what spotipy does 

# this can be the new user method 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm() # have login form return username 
    # check if exists already, if not, then go to spotify login 
    if form.validate_on_submit():
        
        new_username = form.username.data
        session['new_username']= new_username

        remember_me = form.remember_me.data

        # TODO: check that desired username is unique by querying database and verifying no matches 

        # response is the redirect url to Spotify permission page
        response = startup.getUser()  
        return redirect(response) # user is redirected from Spotify back to /callback

    return render_template('login.html', form=form)

    # write the user's access token somewhere in database
    # change how spotifyUser is initialized 
    
    #this is the code to run authentication through the folder structure




#this code gets the access token and returns to auth the access token that was 
#previously stored in .cache thing. so the auth method getAccesstoken will store
#all the access token from everybody who gives us permision. 
@app.route('/callback/')
def callback():
    user_auth_code = request.args['code']
    # exchange user_auth_code for access token, refresh token
    user_token_data = startup.getUserToken(code=user_auth_code)

    #when we change how spotifyUser is initialized. 
    new_user = SpotifyUser(username=session.get("new_username", None), 
                           from_scratch=False, 
                           token=user_token_data[0])

    new_user_data = clean_all_data(new_user=new_user, 
                                   user_token_data=user_token_data)

    insert_new_user_to_database(new_user_data=new_user_data, 
                                db_engine=db.engine)

    return redirect('/')


@app.route('/database', methods=['GET', 'POST'])
def database():
    listener_names = db.session.query(d04_app.models.Listeners.display_name)
    dropdown_list = []
    for listener in listener_names:
        dropdown_list.append(listener[0])
    form = forms.artistsform.form(dropdown_list)#artistsforms is just the name of the form.
    if form.validate_on_submit():
        return redirect('/artistpage/'+ form.listener_sel.data) # not sure if this is right
    return render_template('database.html', dropdown_list=dropdown_list, form=form)


@app.route('/artistpage/<listener_name>', methods=['GET', 'POST'])
def artistpage(listener_name):
    return render_template('artistpage.html')

#this is eventually the route page  we will need.
#@app.route('/artistpage/<artist_name>', methods=['GET', 'POST'])
#def artistpage():
#    return render_template('artistpage.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)