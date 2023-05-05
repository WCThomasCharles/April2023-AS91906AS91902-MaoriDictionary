from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = "C:/Users/garet/OneDrive/Desktop/Thom/Programming/" \
           "GitHub Projects/April2023-AS91906AS91902-MaoriDictionary/dictionary.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "y4nm1e1w4cz3r3a"


def is_logged_in():  # Checks if the user is logged in
    if session.get("email") is None:
        return False
    else:
        print("logged in")
        return True


def create_connection(db_file):  # Creates a connection to the database
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except Error as e:
        print(e)
    return None


@app.route('/')
def render_home():  # Takes the user to the home page
    return render_template('home.html', logged_in=is_logged_in())


@app.route('/login', methods=['POST', 'GET'])
def render_login():  # takes the user to the login page
    if is_logged_in():
        return redirect("/")
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        query = """SELECT PK, Firstname, Hashpass FROM users WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()
        cur.execute(query, (email, ))
        user_data = cur.fetchall()[0]
        con.close()
        print(user_data)
        try:
            user_id = user_data[0]
            first_name = user_data[1]
            hashpass = user_data[2]
        except IndexError:
            print("dataError")
            return redirect("/login?error=Invalid+username+or+password")
        if not bcrypt.check_password_hash(hashpass, password):
            print("passwordError")
            return redirect(request.referrer + "?error=Invalid+username+or+password")

        session['email'] = email
        session['userid'] = user_id
        session['firstname'] = first_name
        print(session)
        return redirect('/')
    return render_template('login.html', logged_in=is_logged_in())


@app.route('/logout')
def logout():
    print(list(session.keys()))
    [session.pop(key) for key in list(session.keys())]
    print(list(session.keys()))
    return redirect('/?message=See+you+next+time!')


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():  # takes the user to the signup page and gathers their signup info
    if is_logged_in():
        return redirect("/")
    if request.method == 'POST':
        print(request.form)
        first_name = request.form.get('Firstname').title().strip()
        last_name = request.form.get('Lastname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')

        if password != password2:
            return redirect("/signup?error=Passwords+do+not+match")
        if len(password) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+characters")

        hashed_password = bcrypt.generate_password_hash(password)
        con = create_connection(DATABASE)
        query = "INSERT INTO users (Firstname, Lastname, Email, Hashpass) VALUES (?, ?, ?, ?)"
        cur = con.cursor()

        try:
            cur.execute(query, (first_name, last_name, email, hashed_password))
        except sqlite3.IntegrityError:
            con.close()
            return redirect("/signup?error=Email+is+already+used")

        con.commit()
        con.close()
        return redirect('/login')

    return render_template("signup.html", logged_in=is_logged_in())


@app.route('/categories')
def render_categories():  # Takes the user to a list of links to categories
    query = "SELECT PK, Category " \
            "FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="category", logged_in=is_logged_in())


@app.route('/category/<category_id>')  # Takes the user to a list of links to words
def render_category(category_id):  # Takes the user to the home page
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where Category = " + category_id
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in())


@app.route('/levels')
def render_levels():  # Takes the user to a list of links to levels
    query = "SELECT PK, level " \
            "FROM levels"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', next_step="level", passed_data=data, logged_in=is_logged_in())


@app.route('/level/<level_id>')
def render_level(level_id):  # Takes the user to a list of links to words
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where level = " + level_id
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in())


@app.route('/word/<word_id>')
def render_entry(word_id):  # # Takes the user to a page for details on a word
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
    return render_template('entry.html', passed_data=data, logged_in=is_logged_in())


if __name__ == '__main__':
    app.run()
