from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import d04_app.forms as forms
import d04_app.startup as startup
import d04_app.authentication as authentication

# import pandas as pd	
# import numpy as np	
# from pandas.io.json import json_normalize	
# from IPython.display import display	
# from d01_data_processing.data_cleaning import *	
# from d01_data_processing.spotify_user import SpotifyUser	
# from d00_utils.load_confs import load_credentials	
	
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm() # have login form return username 
    # check if exists already, if not, then go to spotify login 
    if form.validate_on_submit():
        
        username = form.username.data
        remember_me = form.remember_me.data

        response = startup.getUser()# response is the redirect url to Spotify permission page 
        return redirect(response)

    return render_template('login.html', form=form)

    # write the user's access token somewhere in database
    # change how spotifyUser is initialized 
    
    #when we change how spotifyUser is initialized. 
    #new_user = SpotifyUser(token,	new_username)

    #this is the code to run authentication through the folder structure

    



#this code gets the access token and returns to auth the access token that was 
#previously stored in .cache thing. so the auth method getAccesstoken will store
#all the access token from everybody who gives us permision. 
@app.route('/callback/')
def callback():
    startup.getUserToken(request.args['code'])
    #** I redirect to my homepage here **


@app.route('/database', methods=['GET', 'POST'])
def database():
    artist_names = db.session.query(d04_app.models.Artists.artist_name) 
    dropdown_list = []
    for artist in artist_names:
        dropdown_list.append(artist[0])
    form = forms.artistsform.form(dropdown_list)
    if form.validate_on_submit():
        return redirect('/artistpage') # not sure if this is right
    return render_template('database.html', dropdown_list=dropdown_list, form=form)


@app.route('/artistpage', methods=['GET', 'POST'])
def artistpage():
    return render_template('artistpage.html')

#this is eventually the route page  we will need.
#@app.route('/artistpage/<artist_name>', methods=['GET', 'POST'])
#def artistpage():
#    return render_template('artistpage.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)