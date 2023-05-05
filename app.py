from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = "C:/Users/garet/OneDrive/Desktop/Thom/Programming/" \
           "GitHub Projects/April2023-AS91906AS91902-MaoriDictionary/dictionary.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "y4nm1e1w4cz3r3a"


def create_connection(db_file):  # Creates a connection to the database
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_home():  # Takes the user to the home page
    return render_template('home.html')  # , logged_in=is_logged_in())


@app.route('/categories')
def render_categories():  # Takes the user to the home page
    query = "SELECT PK, Category " \
            "FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="category")  # , logged_in=is_logged_in())


@app.route('/category/<category_id>')
def render_category(category_id):  # Takes the user to the home page
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where Category = " + category_id
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word")  # , logged_in=is_logged_in())


@app.route('/levels')
def render_levels():  # Takes the user to the home page
    query = "SELECT PK, level " \
            "FROM levels"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', next_step="level", passed_data=data)  # , logged_in=is_logged_in())


@app.route('/level/<level_id>')
def render_level(level_id):  # Takes the user to the home page
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where level = " + level_id
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word")  # , logged_in=is_logged_in())


@app.route('/word/<word_id>')
def render_entry(word_id):  # Takes the user to the home page
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT Maori, English, Category, Definition, Level " \
            "FROM words " \
            "Where PK = " + word_id
    cur.execute(query)
    data = list(cur.fetchall()[0])
    query = "SELECT Category " \
            "FROM Categories " \
            "Where PK = " + str(data[2])
    cur.execute(query)
    category = list(cur.fetchall()[0])
    data[2] = category[0]
    query = "SELECT level " \
            "FROM levels " \
            "Where PK = " + str(data[4])
    cur.execute(query)
    level = list(cur.fetchall()[0])
    data[4] = level[0]
    con.close()
    return render_template('entry.html', passed_data=data)  # , logged_in=is_logged_in())


if __name__ == '__main__':
    app.run()
