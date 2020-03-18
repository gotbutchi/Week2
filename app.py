from bs4 import BeautifulSoup
from flask import Flask, render_template, url_for, request, redirect, g

import requests
import sqlite3
import re

app = Flask(__name__)
app.config['TESTING'] = True

BASE_URL = 'https://tiki.vn/'

DATABASE = 'tiki.db'


def get_db():
    """create a database connection to the SQLite database
    """ 
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# home page   
@app.route('/')
def index():
    conn = get_db()
    cur = conn.cursor()
    # get the main parent name
    parent_name = cur.execute("""SELECT name FROM categories WHERE id = 10;""").fetchone()
    # get the subcate name
    sub_cats = cur.execute("""SELECT DISTINCT c1.name FROM categories AS c1 LEFT JOIN categories AS c2 ON c1.id = c2.parent_id WHERE c1.id BETWEEN 100 AND 113;""").fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', parent_name = parent_name, sub_cats = sub_cats)


@app.route('/subcat1')
def index1():
    conn = get_db()
    cur = conn.cursor()
    # get the main parent name
    parent_name = cur.execute("""SELECT DISTINCT c1.name FROM categories AS c1 LEFT JOIN categories AS c2 ON c1.id = c2.parent_id WHERE c1.id = 100;""").fetchone()
    # get the subcate name
    sub_cats = cur.execute("""SELECT DISTINCT c1.name FROM categories AS c1 LEFT JOIN categories AS c2 ON c1.id = c2.parent_id WHERE c1.parent_id = 100;""").fetchall()
    products = cur.execute("""SELECT * FROM product LIMIT 20;""").fetchall()
    # for product in products:
    #     print(product[2])
    cur.close()
    conn.close()
    return render_template('index.html', parent_name = parent_name, sub_cats = sub_cats, products = products)


@app.route('/subcat2')
def index2():
    conn = get_db()
    cur = conn.cursor()
    # get the main parent name
    parent_name = cur.execute("""SELECT DISTINCT c1.name FROM categories AS c1 LEFT JOIN categories AS c2 ON c1.id = c2.parent_id WHERE c1.parent_id = 100;""").fetchone()
    # get the subcate name
    sub_cats = cur.execute("""""").fetchall()
    products = cur.execute("""SELECT * FROM product WHERE cat_id = 700;""").fetchall()
    cur.close()
    conn.close()
    return render_template('index1.html', parent_name = parent_name, sub_cats = sub_cats, products = products)

# def search():
#     conn = get_db()
#     cur = conn.cursor()
#     return render_template('search.html')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)