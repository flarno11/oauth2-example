# Python standard libraries
import json
import os
import requests

# Third-party libraries
from flask import Flask, redirect, request, url_for
from oauthlib.oauth2 import WebApplicationClient

# Configuration
CLIENT_ID = os.environ.get("CLIENT_ID", None)
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", None)
DISCOVERY_URL = os.environ.get("OPENID_DISCOVERY_URL", None)
SCOPES = os.environ.get("OPENID_SCOPES", "openid,email").split(',')

# Flask app setup
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY") or os.urandom(24)

# OAuth 2 client setup
client = WebApplicationClient(CLIENT_ID)


@app.route("/")
def index():
    return '<a class="button" href="/login">Login</a>'


def get_provider_cfg():
    return requests.get(DISCOVERY_URL).json()


@app.route("/login")
def login():
    # Find out what URL to hit for the login
    provider_cfg = get_provider_cfg()
    authorization_endpoint = provider_cfg["authorization_endpoint"]

    # Use library to construct the request for the login and provide
    # scopes that let you retrieve user's profile
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=SCOPES,
    )
    return redirect(request_uri)


@app.route("/login/callback")
def callback():
    # Get authorization code the oauth2 provider sent back to you
    code = request.args.get("code")

    # Find out what URL to hit to get tokens that allow you to ask for
    # things on behalf of a user
    provider_cfg = get_provider_cfg()
    token_endpoint = provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(CLIENT_ID, CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # that gives you the user's profile information
    userinfo_endpoint = provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # You want to make sure their email is verified.
    # The user authenticated, authorized your app, and now you've verified their email!
    if not userinfo_response.json().get("email_verified"):
        return "User email not available or not verified.", 400

    return (
        "<p>Hello, you're logged in!</p>"
        "<p>token response:</p><code>{}</code><br /><br />"
        "<p>userinfo response:</p><code>{}</code><br /><br />"
        '<a class="button" href="/">Start over</a>'.format(
            token_response.json(), userinfo_response.json()
        )
    )


if __name__ == "__main__":
    app.run(ssl_context="adhoc")
