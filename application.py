from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, joinedload
from catalog import *

from flask import session as login_session
import random
import string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Catalog-App Application"

app = Flask(__name__)


engine = create_engine('sqlite:///categoriesitems.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app.secret_key = b'_8#y2L"F4Q8z\n\xec]/'

@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)

@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1].decode('utf-8'))
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect("/")

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print(data)

    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome! '
    flash("You are now logged in with %s as your email address." % login_session['email'])
    return login_session['email']

@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response = make_response(json.dumps('Current user is not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    print('In gdisconnect access token is %s', access_token)
    print(login_session)
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['email']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/JSON')
def categoriesJSON():
    categories = session.query(Categories).options(
        joinedload(Categories.items)).all()
    return jsonify(
        Categories=[
            dict(
                c.serialize,
                items=[
                    i.serialize for i in c.items]) for c in categories])

@app.route('/catalog/<category_name>/JSON')
def categoryJSON(category_name):
    category = session.query(Categories).filter_by(name=category_name).first()
    return jsonify(category=category.serialize)

@app.route('/')
@app.route('/catalog')
def showCatalog():
    categories = session.query(Categories).all()
    items = session.query(Items).all()
    session.commit()
    return render_template('catalog.html', categories=categories, items=items)


@app.route('/catalog/<category_name>/')
def categoryItems(category_name):
    categories = session.query(Categories).all()
    category = session.query(Categories).filter_by(name=category_name).first()
    items = session.query(Items).filter_by(category_name=category_name).all()

    return render_template('items.html', categories=categories, category=category, items=items)


@app.route('/catalog/<category_name>/<item_title>')
def showItem(item_title, category_name):
    item = session.query(Items).filter_by(title=item_title).first()
    category = session.query(Categories).filter_by(name=category_name).first()

    return render_template('item.html', item=item, category=category)

@app.route('/catalog/new', methods=['GET', 'POST'])
def newItem():
    if 'gplus_id' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newItem = Items(
            title=request.form['title'], description=request.form['description'], category_name=request.form['category_name'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html')

@app.route('/catalog/<category_name>/<item_title>/edit',
           methods=['GET', 'POST'])
def editItem(category_name, item_title):
    if 'gplus_id' not in login_session:
        return redirect('/login')
    editedItem = session.query(Items).filter_by(title=item_title).one()
    if request.method == 'POST':
        if request.form['title']:
            editedItem.title = request.form['title']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['category_name']:
            editedItem.category_name = request.form['category_name']
        session.add(editedItem)
        session.commit()
        return redirect(url_for('categoryItems', category_name=category_name))
    else:
        return render_template(
            'edititem.html', category_name=category_name, item_title=item_title, item=editedItem)

@app.route('/catalog/<category_name>/<item_title>/delete',
           methods=['GET', 'POST'])
def deleteItem(category_name, item_title):
    if 'gplus_id' not in login_session:
        return redirect('/login')
    itemToDelete = session.query(Items).filter_by(id=item_title).one()
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        return redirect(url_for('categoryItems', category_name=category_name))
    else:
        return render_template('deleteitem.html', item=itemToDelete)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
