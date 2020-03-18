from bs4 import BeautifulSoup
from collections import deque
import requests
import sqlite3
import time

TIKI_URL = "https://tiki.vn"

#create connection
conn = sqlite3.connect('tiki.db', timeout=5)
cur = conn.cursor()

def create_categories_table():
    query = """
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url TEXT, 
            parent_id INT, 
            create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    try:
        cur.execute(query)
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)
create_categories_table()

class Category:
    def __init__(self, cat_id, name, url, parent_id):
        self.cat_id = cat_id
        self.name = name
        self.url = url
        self.parent_id = parent_id

    def __repr__(self):
        return "ID: {}, Name: {}, URL: {}, Parent_id: {}".format(self.cat_id, self.name, self.url, self.parent_id)

    def save_into_db(self):
        query = """
            INSERT INTO categories (name, url, parent_id)
            VALUES (?, ?, ?);
        """
        val = (self.name, self.url, self.parent_id)
        try:
            cur.execute(query, val)
            self.cat_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)

def get_url(url):
    time.sleep(1)
    try:
        response = requests.get(url).text
        response = BeautifulSoup(response, 'html.parser')
        return response
    except Exception as err:
            print('ERROR BY REQUEST:', err)

def get_main_categories(save_db=False):
    soup = get_url(TIKI_URL)

    result = []
    for a in soup.findAll('a', {'class':'MenuItem__MenuLink-tii3xq-1 efuIbv'}):
        cat_id = None
        name = a.find('span', {'class':'text'}).text
        url = a['href']
        parent_id = None

        cat = Category(cat_id, name, url, parent_id)
        if save_db:
            cat.save_into_db()
        result.append(cat)
    return result

def get_sub_categories(category, save_db=False):
    name = category.name
    url = category.url
    result = []

    try:
        soup = get_url(url)
        div_containers = soup.findAll('div', {'class':'list-group-item is-child'})
        for div in div_containers:
            sub_id = None
            sub_name = div.a.text
            sub_url = 'http://tiki.vn' + div.a['href']
            sub_parent_id = category.cat_id

            sub = Category(sub_id, sub_name, sub_url, sub_parent_id)
            if save_db:
                sub.save_into_db()
            result.append(sub)
    except Exception as err:
        print('ERROR BY GET SUB CATEGORIES:', err)

    return result

def get_all_categories(main_categories):
    de = deque(main_categories)
    count = 0

    while de:
        parent_cat = de.popleft()
        sub_cats = get_sub_categories(parent_cat, save_db=True)
        # print(sub_cats)
        de.extend(sub_cats)
        count += 1

        if count % 100 == 0:
            print(count, 'times')

#create a product table
#refer to the sub category with foreign key
def create_product_table():
    query = """
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            url TEXT,
            img_url TEXT,
            regular_price TEXT,
            final_price TEXT,            
            sale_tag TEXT,
            comment INT,
            rating TEXT,
            cat_id INT,
            FOREIGN KEY(cat_id) REFERENCES categories(parent_id)
            );
    """
    try:
        cur.execute(query)
    except Exception as err:
        print('ERROR BY CREATE TABLE', err)
create_product_table()

class Product():
    def __init__(self, product_id, name, url, img_url, regular_price, final_price, sale_tag, comment, rating, cat_id):
        self.product_id = product_id
        self.name = name
        self.url = url
        self.img_url = img_url
        self.regular_price = regular_price
        self.final_price = final_price
        self.sale_tag = sale_tag
        self.comment = comment
        self.rating = rating
        self.cat_id = cat_id

    def __repr__(self):
        return "ID: {}, Name: {}, URL: {}, Img_URL: {}, regular_price: {}, final_price: {}, sale_tag: {}, comment: {}, rating: {}, cat_id: {}".format(self.product_id, self.name, self.url, self.igm_url, self.regular_price, self.final_price, self.sale_tag, self.comment, self.rating, self.cat_id)

    def save_into_db(self):
        query = """
            INSERT INTO product (name, url, img_url, regular_price, final_price, sale_tag, comment, rating, cat_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """
        val = (self.name, self.url, self.img_url, self.regular_price, self.final_price, self.sale_tag, self.comment, self.rating, self.cat_id)
        try:
            cur.execute(query, val)
            self.product_id = cur.lastrowid
            conn.commit()
        except Exception as err:
            print('ERROR BY INSERT:', err)

#get only the categories of makeup which dont have any child category
# def get_product(save_db=False):
#     query = """
#     SELECT id, name, url FROM categories
#     WHERE parent_id BETWEEN 100 AND 113;
#     """
#     try:
#         cur.execute(query)
#     except Exception as err:
#         print('ERROR BY SELECT TABLE', err)

#     rows = cur.fetchall()
    
#     for i in rows:
#         id = i[0]
#         name = " ".join(i[1].strip().split()[:-1])
#         url = i[2].strip()
#         for page in range(1,4):
#             page_url = url + "&page=" + str(page)
# #             print(page_url)
#             page_html = get_url(page_url)
#             products_wrapper_div = page_html.find_all('div', class_='product-box-list')[0]
#             products_div = products_wrapper_div.find_all('div', class_='product-item')
#             result = []
#             if len(products_div) > 0:
#                 for product_div in products_div:
#                     product_id = None
#                     title = product_div.a['title']
#                     url = product_div.a['href']
#                     img_url = product_div.img['src']
#                     regular_price = product_div.find('span', class_='price-regular').text
#                     final_price = product_div.find('span', class_='final-price').text.split()[0]
#                     sale_tag = product_div.find('span', class_='sale-tag').text
#                     comment = product_div.find('p', class_='review').text.split()[0] + ' review(s))'
#                     rating = product_div.find('span', class_='rating-content').span['style'].split(":")[-1]
#                     product = Product(product_id, name, url, img_url, regular_price, final_price, sale_tag, comment, rating, id)
                
#                     if save_db:
#                         product.save_into_db()
#                         print(f'SAVE {title} INTO DTB')
#                     result.append(product)
#             else:
#                 break

#get only the categories of makeup which dont have any child category
def get_product(save_db=False):
    query = """
    SELECT id, name, url FROM categories
    WHERE parent_id BETWEEN 100 AND 113;
    """
    try:
        cur.execute(query)
    except Exception as err:
        print('ERROR BY SELECT TABLE', err)

    rows = cur.fetchall()
    
    for i in rows:
        id = i[0]
        name = " ".join(i[1].strip().split()[:-1])
        url = i[2].strip()
        for page in range(1,4):
            page_url = url + "&page=" + str(page)
#             print(page_url)
            page_html = get_url(page_url)
            try:
                products_wrapper_div = page_html.find_all('div', class_='product-box-list')[0]
            except Exception as err:
                 print('ERROR BY DIV FINDALL: ', err)
            if products_wrapper_div:
                products_div = products_wrapper_div.find_all('div', class_='product-item')
                result = []
                if len(products_div) > 0:
                    for product_div in products_div:
                        product_id = None
                        title = product_div.a['title']
                        url = product_div.a['href']
                        img_url = product_div.img['src']
                        regular_price = product_div.find('span', class_='price-regular').text
                        final_price = product_div.find('span', class_='final-price').text.split()[0]
                        sale_tag = product_div.find('span', class_='sale-tag').text
                        comment = product_div.find('p', class_='review').text.split()[0] + ' review(s))'
                        if product_div.find('span', class_='rating-content'):
                            rating = product_div.find('span', class_='rating-content').find('span')['style'].split(":")[-1]
                        else:
                            rating = '0%'
                        product = Product(product_id, title, url, img_url, regular_price, final_price, sale_tag, comment, rating, id)

                        if save_db:
                            product.save_into_db()
                            print(f'SAVE {title} INTO DB')
                        result.append(product)
                else:
                    break

get_product()