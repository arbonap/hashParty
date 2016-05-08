#Standard Library Imports
import os

#Related Third Party Imports
from flask import Flask, render_template, request, session, jsonify
import requests
#pretty print it up
from pprint import pprint
import time
import datetime



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
    hashtag = request.form.get('hashtag')
    print "Hashtag:", hashtag
    endpoint = "https://api.instagram.com/v1/tags/changetheratio/media/recent?access_token={}".format(session['user_token'])
    print "************************************************"
    print "endpoint:", endpoint

    resp = requests.get(endpoint)
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    print "RESP:", resp
    response_dict = resp.json()
    print "&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&"
    print "Response dictionary:"

    pprint(response_dict)

    startdate = request.form.get('startdate')
    enddate = request.form.get('enddate')

    startdatetime = datetime.datetime.strptime(startdate, "%Y-%m-%d")
    print "Start date:", startdatetime

    start_timestamp = time.mktime(startdatetime.timetuple())
    print "Unix/ Epoch Timestamp!!!", start_timestamp

    enddatetime = datetime.datetime.strptime(enddate, "%Y-%m-%d")
    print "End date:", enddatetime

    end_timestamp = time.mktime(enddatetime.timetuple())
    filtered_results = filter_results(start_timestamp, end_timestamp, hashtag, response_dict)
    #jsonify only works on dictionaries (not on lists?)
    special_thing = jsonify({'thing': filtered_results})
    print "@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@: jsonify special thing @@@@@"
    print special_thing
    return jsonify({'thing': filtered_results})

################################################################################

# The app should paginate through the endpoint and collect the content whose tag time is in
# between the start and end dates only. The photo's tag time is defined as the time that the
# hashtag was tagged with the photo. Normally, that is the caption created time (caption ->
# created_time). However, if the caption does not contain the desired hashtag, but the
# submitter of the photo posts a comment with the desired hashtag afterward, that photo will
# be included in the pagination, under the time the comment was posted. You will want to
# iterate through the comments key for each photo, and look for the existence of the hashtag. If
# found, the created_time of the comment should be used as the tag time:


def filter_results(start, end, tag, results_dict):
    """ Filter through ugly, horrible JSON dictionary to get 'created_time'.
        Given start and end timestamps, return only results within the start and
        end timestamps. """

    # Obtain the list of media results from the response dictionary
    results_list = results_dict['data']

    # Initialize an empty list which will contain tuples of (tag_time, media_dictionary)
    final_results = []

    print "Length of list before starting", len(results_list)
    i = 0
    while i < len(results_list):
        text = results_list[i]['caption']['text']
        #check if tag is in "text" attribute
        print "Index", i
        if text.find(tag) > 0:
            print "tag in caption"
            created_time = int(results_list[i]['caption']['created_time'])
            print "created time", created_time
            if created_time > end or created_time < start:
                print "deleting"
                del results_list[i]
            else:
                print "appending"
                final_results.append({"timestamp": created_time, "media": results_list[i]})
                i += 1
        #else, check the comments key for each photo, and find the hashtag
        else:
            print "tag not in caption"
            media_id = results_list[i]['id']
            endpoint = "https://api.instagram.com/v1/media/{}/comments?access_token={}".format(media_id, session['user_token'])

            resp = requests.get(endpoint)
            resp_dict = resp.json()
            resp_list = resp_dict['data']
            j = 0
            while j < len(resp_list):
                text = resp_list[j]['text']
                if text.find(tag) > 0:
                    final_results.append({"timestamp": resp_list[j]['created_time'], "media": results_list[i]})
                    print "appending"
                    del resp_list[j]
                else:
                    print "deleting"
                    del results_list[i]
                    j += 1
            i += 1

    print "Length of list after filtering", len(results_list)
    return final_results

if __name__ == "__main__":
    app.debug = True

    app.run()
