import os

from flask import Flask, redirect, render_template, request, session, url_for
from requests.exceptions import HTTPError

from hypothesis import HypothesisClient

app = Flask(__name__)
app.secret_key = 'notverysecret'
hypothesis_service = os.environ.get('HYPOTHESIS_SERVICE', 'http://localhost:5000')
hyp_client = HypothesisClient(authority=os.environ['HYPOTHESIS_AUTHORITY'],
                              client_id=os.environ['HYPOTHESIS_CLIENT_ID'],
                              client_secret=os.environ['HYPOTHESIS_CLIENT_SECRET'],
                              service=hypothesis_service)


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    email = '{}@partner.org'.format(username)
    try:
        hyp_client.create_account(username, email=email)
    except HTTPError as ex:
        # FIXME: Make the service respond with an appropriate status code and
        # machine-readable error if the user account already exists
        already_exists_err = 'user with email address {} already exists'.format(email)
        if already_exists_err not in ex.response.content:
            raise ex

    session['username'] = username
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/')
def index():
    username = session.get('username', None)
    grant_token = None

    if username:
        grant_token = hyp_client.grant_token(username=username)

    return render_template('article.html',
                           grant_token=grant_token,
                           username=username,
                           service_url=hypothesis_service)
