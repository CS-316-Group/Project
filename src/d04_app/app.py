from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy

from d00_utils.load_confs import load_parameters
from d01_data_processing.data_cleaning import clean_all_data
from d01_data_processing.spotify_user import SpotifyUser    
import d04_app.forms as forms
import d04_app.startup as startup
from d04_app.db_operations import insert_new_user_to_database
import d04_app.models

app_params = load_parameters()

app = Flask(__name__)
app.secret_key = app_params['secret_key']
app.config.from_object('d04_app.config')
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

        	# if incorrect password

        # if username not in the database 

        # response is the redirect url to Spotify permission page
        response = startup.getUser()  
        return redirect(response) # user is redirected from Spotify back to /callback

    return render_template('returninglogin.html', form=form)

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
    app.run(host='0.0.0.0', port=app_params['port'], debug=True)
