from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
import forms
import startup
#import authentication

app = Flask(__name__)
app.secret_key = 'cs316'
app.config.from_object('config')
db = SQLAlchemy(app, session_options={'autocommit': False})

import models

@app.route('/')
def home():
    return render_template('home.html')
    

@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # form = forms.LoginForm()
    # if form.validate_on_submit():
    #     flash('Login requested for user {}, remember_me={}'.format(
    #         form.username.data, form.remember_me.data))
    #     return redirect('/')#when we figure out hoow to connect to spotify we can redirect here.
    # return render_template('login.html', form=form)
    response = startup.getUser()
    return redirect(response)

    #authentication.autenticate()



#this code gets the access token and returns to auth the access token that was 
#previously stored in .cache thing. so the auth method getAccesstoken will store
#all the access token from everybody who gives us permision. 
@app.route('/callback/')
def callback():
    startup.getUserToken(request.args['code'])
    #** I redirect to my homepage here **


@app.route('/database', methods=['GET', 'POST'])
def database():
    artist_names = db.session.query(models.Artists.artist_name) 
    dropdown_list = []
    for artist in artist_names:
        dropdown_list.append(artist[0])
    form = forms.artistsform.form(dropdown_list)
    if form.validate_on_submit():
        return render_template('artistpage.html') # not sure if this is right
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