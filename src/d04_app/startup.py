import time

from d00_utils.load_confs import load_credentials, load_parameters
from d04_app.auth import getAuth, refreshAuth, getToken

creds = load_credentials()
app_params = load_parameters()

CLIENT_ID= creds['spotify_dev_creds']['spotify_client_id']
CLIENT_SECRET = creds['spotify_dev_creds']['spotify_client_secret']

CALLBACK_URL = app_params['host_url']
SCOPE = app_params['scope']


def getUser():
    '''
    Constructs get request to /authorize endpt of Spotify API
    '''
    return getAuth(client_id=CLIENT_ID, 
                   redirect_uri=f"{CALLBACK_URL}/callback/", 
                   scope=SCOPE)

def getUserToken(code):
    '''
    getUserToken takes the authorization code given to us by the Spotify authorization 
    endpoint and goes back to the Spotify API to get the user access token. 

    Keyword arguments
        code: string authorization code

    Returns
        TOKEN_DATA: a list as follows: [access_token, auth_head, scope, expires_in, refresh_token]
    '''
    TOKEN_DATA = getToken(code=code, 
                          client_id=CLIENT_ID, 
                          client_secret=CLIENT_SECRET, 
                          redirect_uri=f"{CALLBACK_URL}/callback/")
    return TOKEN_DATA 
 

def refreshToken(refresh_token,
                 seconds:int=0):
    '''Using the refresh token, gets an a new access token and refresh 
    token from the Spotify API. 

    Keyword arguments
        refresh_token: string reauthorization code
        seconds: amount of time to wait before executing this function

    Returns
        TOKEN_DATA: a list as follows: [access_token, auth_head, scope, expires_in, refresh_token]
    '''
    time.sleep(seconds)
    TOKEN_DATA = refreshAuth(refresh_token=refresh_token, 
                             client_id=CLIENT_ID, 
                             client_secret=CLIENT_SECRET)
    return TOKEN_DATA
