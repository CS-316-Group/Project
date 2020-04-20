from d00_utils.load_confs import load_credentials, load_parameters
from d04_app.auth import getAuth, refreshAuth, getToken

creds = load_credentials()
app_params = load_parameters()

CLIENT_ID= creds['spotify_dev_creds']['spotify_client_id']
CLIENT_SECRET = creds['spotify_dev_creds']['spotify_client_secret']

#Port and callback url can be changed or left to localhost:5000
PORT = app_params['port']
CALLBACK_URL = app_params['host_url']
SCOPE = app_params['scope']

#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown 
TOKEN_DATA = []


def getUser():
    '''
    Constructs get request to /authorize endpt of Spotify API
    '''
    return getAuth(client_id=CLIENT_ID, 
                   redirect_uri=f"{CALLBACK_URL}:{PORT}/callback/", 
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
    global TOKEN_DATA
    TOKEN_DATA = getToken(code=code, 
                          client_id=CLIENT_ID, 
                          client_secret=CLIENT_SECRET, 
                          redirect_uri=f"{CALLBACK_URL}:{PORT}/callback/")
    return TOKEN_DATA 
 
def refreshToken(time, 
                 refresh_token):
    time.sleep(time)
    TOKEN_DATA = refreshAuth(refresh_token)

def getAccessToken():
    return TOKEN_DATA
