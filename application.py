from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from catalog import *

app = Flask(__name__)


engine = create_engine('sqlite:///categoriesitems.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


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
