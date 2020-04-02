import json, requests

SPOTIFY_URL_AUTH = 'https://accounts.spotify.com/authorize/?'
SPOTIFY_URL_TOKEN = 'https://accounts.spotify.com/api/token/'
RESPONSE_TYPE = 'code'   
HEADER = 'application/x-www-form-urlencoded'
REFRESH_TOKEN = ''
    
def getAuth(client_id, redirect_uri, scope):
    data = f"{SPOTIFY_URL_AUTH}client_id={client_id}&response_type=code&redirect_uri={redirect_uri}&scope={scope}" 
    return data

def getToken(code, client_id, client_secret, redirect_uri):
    body = {
            "grant_type": 'authorization_code',
            "code" : code,
            "redirect_uri": redirect_uri,
            "client_id": client_id,
            "client_secret": client_secret
            }
    
    # creds_bytes =  f"{client_id}:{client_secret}".encode('utf-8')
    # creds_encoded = base64.b64encode(creds_bytes)

    # headers = {"Content-Type" : HEADER, 
               # "Authorization" : f"Basic {creds_encoded}"} 
    headers = {"Content-Type" : HEADER}

    post = requests.post(SPOTIFY_URL_TOKEN, params=body, headers=headers)
    return handleToken(json.loads(post.text))
    
def handleToken(response):
    try:
        auth_head = {"Authorization": "Bearer {}".format(response["access_token"])}
        REFRESH_TOKEN = response["refresh_token"]
    except Exception as e: 
        print("Authorization failed. Response from API was: ", response)

    return [response["access_token"], 
            auth_head, 
            response["scope"], 
            response["expires_in"]]

def refreshAuth():
    body = {
        "grant_type" : "refresh_token",
        "refresh_token" : REFRESH_TOKEN
    }

    post_refresh = requests.post(SPOTIFY_URL_TOKEN, data=body, headers=HEADER)
    p_back = json.dumps(post_refresh.text)
    
    return handleToken(p_back)
