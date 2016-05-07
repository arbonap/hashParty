#Standard Library Imports
import os

#Related Third Party Imports
from flask import Flask, render_template, request, session, jsonify

import requests

app = Flask(__name__)
app.secret_key = os.environ['FLASK_KEY']
################################################################################


@app.route('/', methods=['GET'])
def index():
    """Homepage"""

    return render_template("homepage.html")


@app.route('/instagram_callback', methods=['GET'])
def dashboard():

    code = request.args.get('code')
    print "******************************* "
    print "code used to make access token below: *****"
    print code

    payload = {"client_id": os.environ['CLIENT_ID'],
               "client_secret": os.environ['CLIENT_SECRET'],
               "grant_type": "authorization_code",
               "redirect_uri": "http://localhost:5000/instagram_callback",
               "code": code,
               }

    resp = requests.post("https://api.instagram.com/oauth/access_token", data=payload)
    print "************************************************"
    print "************************************************"
    print "response object", resp
    resp_dict = resp.json()
    print "************************************************"
    print "************************************************"
    print "Response dictionary", resp_dict
    # access_token = resp_dict['access_token']
    user = resp_dict['user']['username']
    print "************************************************"
    print "username:", user
    token = resp_dict['access_token']
    print "Token:", token
    print "************************************************"
    print "************************************************"
    session['user_token'] = token
    print "session:", session
    print "************************************************"
    print "************************************************"
    return render_template("dash.html", user=user)


@app.route('/search', methods=['GET', 'POST'])
def searchresults():
    hashtag = request.args.get('hashtag')
    endpoint = "https://api.instagram.com/v1/tags/{}/media/recent?access_token={}".format(hashtag, session['user_token'])
    print "************************************************"
    print "endpoint:", endpoint

    resp = requests.get(endpoint)
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    print "RESP:", resp
    response_dict = resp.json()
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    print "Response dictionary:"
    print response_dict
    return jsonify(response_dict)

################################################################################
if __name__ == "__main__":
    app.debug = True

    app.run()
