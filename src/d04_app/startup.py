from d04_app.auth import getAuth, refreshAuth, getToken

#Aclient id from downloaded app.
#CLIENT_ID = "98c167e218bd483891f8638caaca19cb"
#bens client id:
CLIENT_ID = "46a21c22c2b84831a61e13aabc27dc30"
#selens:
#CLIENT_ID ="713a065a310b499c93af68eaefb213e7"
#mine
#CLIENT_ID = "975ac8a7753243389c7713dfe121cd52"

#cleint secret id from the downloaded up
#CLIENT_SECRET = "e40d06af72524208bf0bbb048ba299a3"


#ben client id:
CLIENT_SECRET = "3211a9953f4d4facbe8fad5d6b171ea2"
#selens ids.
#CLIENT_SECRET = "c2cdbfa0fcdc4bbb9461638c57a0a41e"
#mine
#CLIENT_SECRET = "df6cdabcedae407fa873427f3947f5bf"

#Port and callback url can be changed or ledt to localhost:5000
PORT = "8889" #intial host but i think ben has only approved 8888.
#PORT = "8888"
CALLBACK_URL = "http://localhost"

#Add needed scope from spotify user
#SCOPE = "streaming user-read-birthdate user-read-email user-read-private"
SCOPE = "user-library-read user-follow-read user-top-read user-read-recently-played"
#SCOPE = "user-read-private"

#token_data will hold authentication header with access code, the allowed scopes, and the refresh countdown 
TOKEN_DATA = []


def getUser():
    return getAuth(CLIENT_ID, "{}:{}/callback/".format(CALLBACK_URL, PORT), SCOPE)

def getUserToken(code):
    global TOKEN_DATA
    TOKEN_DATA = getToken(code, CLIENT_ID, CLIENT_SECRET, "{}:{}/callback/".format(CALLBACK_URL, PORT))
 
def refreshToken(time):
    time.sleep(time)
    TOKEN_DATA = refreshAuth()

def getAccessToken():
    return TOKEN_DATA
