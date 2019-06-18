#!/usr/bin/env python3
from flask import Flask, render_template
from flask import request, redirect, url_for, jsonify, flash
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

from functools import wraps

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


# if user not logged it
def login_required(f):
    """ Check if user is logged in function /

    Returns: /
    - Decorated function to be passed along with add, /
    edit and delete items functions. /
    - If user is not logged in, redirect to login page."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'gplus_id' not in login_session:
            flash('You are not allowed to access there')
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# add user to database
def addUser(login_session):
    """Add connected user to database

      Args: login_session
      Return: user's id
    """
    newUser = Users(
        id=login_session['id'],
        email=login_session['email'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).first()
    return user.id


# get user's id from database
def getUserId(email):
    """Get user's id from database function

      Args: email
      Return: user's id or None
    """
    try:
        user = session.query(Users).filter_by(email=email).first()
        return user.id
    except BaseException:
        return None


# login
@app.route('/login')
def showLogin():
    """Log in function

    Assigns the state of the login_session made of a random string"""
    random_choice = random.choice(string.ascii_uppercase + string.digits)
    state = ''.join(random_choice for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# redirect
@app.route('/gconnect', methods=['GET', 'POST'])
def gconnect():
    """Connect to Google API to log in /

    - Request to Google API for user to log in with their /
        Google account details"""
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
        response_copy = 'Current user is already connected.'
        response = make_response(json.dumps(response_copy),
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
    print('Returned data: ', data)
    # Assign login_session email info
    login_session['email'] = data['email']
    login_session['id'] = data['id']
    # User's details
    user_id = getUserId(login_session['email'])
    if not user_id:
        user_id = addUser(login_session)
    login_session['id'] = user_id

    # Logged in confirmation message for user
    output = ''
    output += '<h1>Welcome! '
    flash_message = "You are now logged in with %s as your email address."
    flash(flash_message % login_session['email'])
    return login_session['email']


# logout
@app.route('/gdisconnect')
def gdisconnect():
    """Log out function

    - Checks if current user is logged in by the access token of the session
    - Makes a request to Google to delete the user's token, /
    id and email from the login_session
    - Redirects to the main page
    """
    access_token = login_session.get('access_token')
    if access_token is None:
        print('Access Token is None')
        response_copy = 'Current user is not connected.'
        response = make_response(json.dumps(response_copy), 401)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    print('In gdisconnect access token is %s', access_token)
    print(login_session)
    url_path = 'https://accounts.google.com/o/oauth2/revoke?token=%s'
    url = url_path % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print('result is ')
    print(result)
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['email']
        del login_session['id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect('/catalog')
    else:
        response_copy = 'Failed to revoke token for given user.'
        response = make_response(json.dumps(response_copy, 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# catalog JSON
@app.route('/catalog/JSON')
def categoriesJSON():
    """ The catalog JSON object

    Returns: /
    - The catalog JSON object which includes all categories and items"""
    categories = session.query(Categories).options(
        joinedload(Categories.items)).all()
    return jsonify(
        Categories=[
            dict(
                c.serialize,
                items=[
                    i.serialize for i in c.items]) for c in categories])


# category JSON
@app.route('/catalog/<category_name>/JSON')
def categoryJSON(category_name):
    """ The category JSON object

    Args: category_name

    Returns: /
    - A given category JSON object with its details - name, id, items"""
    category = session.query(Categories).filter_by(name=category_name).first()
    items = session.query(Items).filter_by(category_name=category_name).all()

    return jsonify(
            dict(
                category=category.serialize,
                items=[
                    i.serialize for i in items]))


# item JSON
@app.route('/catalog/<category_name>/<item_title>/JSON')
def itemJSON(item_title, category_name):
    """ The category's item JSON object

    Args: item_title, category_name

    Returns: /
    - A given item JSON object from a given category"""
    item = session.query(Items).filter_by(title=item_title).first()
    return jsonify(item=item.serialize)


# catalog page
@app.route('/')
@app.route('/catalog')
def showCatalog():
    """Show all categories and items function

    Returns:
    - The catalog's all categories and items
    """
    categories = session.query(Categories).all()
    items = session.query(Items).all()
    session.commit()
    return render_template('catalog.html', categories=categories, items=items)


#  category page
@app.route('/catalog/<category_name>/')
def categoryItems(category_name):
    """Show all items of a category function

    Args: category_name

    Returns:
    - All items of a specific category
    """
    categories = session.query(Categories).all()
    category = session.query(Categories).filter_by(name=category_name).first()
    items = session.query(Items).filter_by(category_name=category_name).all()
    html = 'items.html'
    return render_template(
        html,
        categories=categories,
        category=category,
        items=items)


# item page
@app.route('/catalog/<category_name>/<item_title>')
def showItem(item_title, category_name):
    """Show an item's details function

    Args: category_name, items_title

    Returns:
    - A specific item's details - title and description
    """
    item = session.query(Items).filter_by(title=item_title).first()
    category = session.query(Categories).filter_by(name=category_name).first()

    return render_template('item.html', item=item, category=category)


# add item
@app.route('/catalog/new', methods=['GET', 'POST'])
@login_required
def newItem():
    """Add a new item to the database function

    - Check if user is allowed to add items - if logged in
    - Add item's details to the database - title, description, category /
        name and author
    - Redirect to main page when form submission is completed
    """
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category_name = request.form['category_name']
        newItem = Items(
            title=title,
            description=description,
            category_name=category_name,
            user_id=login_session['id'])
        session.add(newItem)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newitem.html')


# edit item
@app.route('/catalog/<category_name>/<item_title>/edit',
           methods=['GET', 'POST'])
@login_required
def editItem(category_name, item_title):
    """Edit item's details function

    Args: category_name, item_title

    - Check if user is allowed to edit item - if logged in
    - Check if user is authorized to edit item - if item's author /
    - User edits any of item's details - title, description,
        category name
    - Redirect to category items after form is submitted
    """
    editedItem = session.query(Items).filter_by(title=item_title).one()
    if int(editedItem.user_id) == login_session['id']:
        if request.method == 'POST':
            if request.form['title']:
                editedItem.title = request.form['title']
            if request.form['description']:
                editedItem.description = request.form['description']
            if request.form['category_name']:
                editedItem.category_name = request.form['category_name']
            session.add(editedItem)
            session.commit()
            url = url_for('categoryItems', category_name=category_name)
            return redirect(url)
        else:
            html = 'edititem.html'
            return render_template(
                html,
                category_name=category_name,
                item_title=item_title,
                item=editedItem)
    else:
        url = url_for('categoryItems', category_name=category_name)
        return redirect(url)


# delete item
@app.route('/catalog/<category_name>/<item_title>/delete',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category_name, item_title):
    """Delete item from the database function

    Args: category_name, item_title

    - Check if user is allowed to delete item - if logged in
    - Check if user is authorized to delete item - if item's author /
    - User deletes selected item from the database
    - Redirect to category items after form is submitted
    """
    itemToDelete = session.query(Items).filter_by(title=item_title).one()
    # delete item
    if int(itemToDelete.user_id) == login_session['id']:
        if request.method == 'POST':
            session.delete(itemToDelete)
            session.commit()
            # redirect to category page
            url = url_for('categoryItems', category_name=category_name)
            return redirect(url)
        else:
            return render_template('deleteitem.html', item=itemToDelete)
    else:
        url = url_for('categoryItems', category_name=category_name)
        return redirect(url)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
