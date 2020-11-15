# OAuth2 OpenID Demo App

Simple Flask app which does the OAuth2 authorization code flow.

Based on https://realpython.com/flask-google-login/


## Setup

Register a new OAuth2 App at your OAuth2 provider to retrieve a CLIENT_ID and CLIENT_SECRET.
During the registration, specify https://localhost:5000/login/callback as your REDIRECT_URL. 

## Run app

    export CLIENT_ID=Your OAuth2 Client ID
    export CLIENT_SECRET=Your OAuth2 Client Secret
    export OPENID_DISCOVERY_URL=The OAuth2 .well-known/openid-configuration Url, e.g. https://accounts.google.com/.well-known/openid-configuration
    export OPENID_SCOPES=Comma separated scopes to request, e.g. openid,email,profile. To get a refresh token, add offline_access
    
    python3 -m venv venv
    pip install -r requirements.txt
    source venv/bin/activate
    python3 app.py
