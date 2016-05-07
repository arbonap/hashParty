#Standard Library Imports
import os

#Related Third Party Imports
from flask import Flask, render_template, request

import requests

app = Flask(__name__)
app.secret_key = os.environ['FLASK_KEY']
################################################################################


@app.route('/', methods=['GET'])
def index():
    """Homepage"""

    return render_template("homepage.html")


@app.route('/dash', methods=['GET'])
def dashboard():

    code = request.args.get('code')
    print code

    payload = {"client_id": os.environ['INSTAGRAM_ID'],
               "client_secret": os.environ['INSTAGRAM_SECRET'],
               "grant_type": "authorization_code",
               "redirect_uri": "http://localhost:5000/dash",
               "code": code,
               }

    resp = requests.post("https://api.instagram.com/oauth/access_token", data=payload)

    resp_dict = resp.json()
    print resp_dict
    # access_token = resp_dict['access_token']
    user = resp_dict['user']['username']
    print user

    return render_template("dash.html", user=user)

################################################################################
if __name__ == "__main__":
    app.debug = True

    app.run()
