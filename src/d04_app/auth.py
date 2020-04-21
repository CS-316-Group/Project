import json, requests

SPOTIFY_URL_AUTH = 'https://accounts.spotify.com/authorize/?'
SPOTIFY_URL_TOKEN = 'https://accounts.spotify.com/api/token/'
RESPONSE_TYPE = 'code'   
HEADER = 'application/x-www-form-urlencoded'
    

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
    # alt way to provide client_id, client_secret
    #encoded_oauth2_tokens = base64.b64encode('{}:{}'.format(client_id, client_secret).encode())
    #headers = {"Authorization": "Basic {}".format(encoded_oauth2_tokens.decode())}

    headers = {"Content-Type" : HEADER}

    post = requests.post(SPOTIFY_URL_TOKEN, params=body, headers=headers)
    if post.status_code != 200:
        raise Exception("Request for access token from Spotify API failed.")

    return handleToken(json.loads(post.text))

    
def handleToken(response):
    try:
        auth_head = {"Authorization": "Bearer {}".format(response["access_token"])}

    except Exception as e: 
        print("Authorization failed. Response from API was: ", response)

    return [response["access_token"],
            auth_head,
            response["scope"],
            response["expires_in"],
            response["refresh_token"]]


def refreshAuth(refresh_token, client_id, client_secret):
    body = {
        "grant_type" : "refresh_token",
        "refresh_token" : refresh_token,
        "client_id": client_id,
        "client_secret": client_secret
    }

    headers = {"Content-Type" : HEADER}

    post_refresh = requests.post(SPOTIFY_URL_TOKEN, data=body, headers=headers)

    if post_refresh.status_code != 200: 
        raise Exception("Request for refresh token from Spotify API failed.")

    p_back = json.loads(post_refresh.text)
    p_back["refresh_token"] = refresh_token

    return handleToken(p_back)
