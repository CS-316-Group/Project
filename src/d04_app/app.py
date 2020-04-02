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
        # check if exists already, if not, then go to spotify login 
        # response is the redirect url to Spotify permission page
        response = startup.getUser()  
        return redirect(response) # user is redirected from Spotify back to /callback

    return render_template('login.html', form=form)




@app.route('/callback/')
def callback():

    startup.getUserToken(request.args['code'])
    return render_template('home.html')


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