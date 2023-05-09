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

        query = """SELECT PK, Firstname, Hashpass, Admin FROM users WHERE email = ?"""
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
            admin = user_data[3]
        except IndexError:
            print("dataError")
            return redirect("/login?error=Invalid+username+or+password")
        if not bcrypt.check_password_hash(hashpass, password):
            print("passwordError")
            return redirect(request.referrer + "?error=Invalid+username+or+password")

        session['email'] = email
        session['userid'] = user_id
        session['firstname'] = first_name
        session['admin'] = admin
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


@app.route('/admin')
def render_admin():
    if not is_logged_in():
        return redirect('/')
    query = "SELECT Category " \
            "FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    categories = cur.fetchall()
    query = "SELECT level " \
            "FROM levels"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    levels = cur.fetchall()
    con.close()
    return render_template('admin.html', categories=categories, levels=levels, logged_in=is_logged_in())


@app.route('/add/<table>/<column>', methods=['POST', 'GET'])
def add(table, column):
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        print(request.form)
        name = request.form.get('name').title().strip()
        print(name)
        user = session.get("userid")
        con = create_connection(DATABASE)
        query = "INSERT INTO " + table + " (" + column + ", User) VALUES (?, ?)"
        cur = con.cursor()
        cur.execute(query, (name, user))
        con.commit()
        con.close()
        return redirect('/admin')


@app.route('/addword', methods=['POST', 'GET'])
def add_word():
    if not is_logged_in():
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        maori = request.form.get('maori').title().strip()
        english = request.form.get('english').title().strip()
        definition = request.form.get('definition').title().strip()
        category = request.form.get('category').title().strip()
        level = request.form.get('level').title().strip()
        user = session.get("userid")
        con = create_connection(DATABASE)
        query = "INSERT INTO words (Maori, English, Category, Definition, Level, Owner) VALUES (?, ?, ?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query, (maori, english, category, definition, level, user))
        con.commit()
        con.close()
        return redirect('/admin')


@app.route('/editer/<word>')
def render_editer(word):
    if not is_logged_in():
        return redirect('/')
    return render_template('editer.html', logged_in=is_logged_in())


@app.route('/categories')
def render_categories():  # Takes the user to a list of links to categories
    query = "SELECT PK, Category " \
            "FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    title = "Categories"
    return render_template('href_list.html', passed_data=data, next_step="category", logged_in=is_logged_in(), title=title)


@app.route('/category/<category_id>')  # Takes the user to a list of links to words
def render_category(category_id):  # Takes the user to the home page
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where Category = " + category_id
    cur.execute(query)
    data = cur.fetchall()
    query = "SELECT Category " \
            "FROM Categories " \
            "Where PK = " + category_id
    cur.execute(query)
    title = str(cur.fetchone()[0])
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in(), title=title)


@app.route('/levels')
def render_levels():  # Takes the user to a list of links to levels
    query = "SELECT PK, level " \
            "FROM levels"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    data = cur.fetchall()
    con.close()
    title = "Levels"
    return render_template('href_list.html', next_step="level", passed_data=data, logged_in=is_logged_in(), title=title)


@app.route('/level/<level_id>')
def render_level(level_id):  # Takes the user to a list of links to words
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where level = " + level_id
    cur.execute(query)
    data = cur.fetchall()
    query = "SELECT level " \
            "FROM levels " \
            "Where PK = " + level_id
    cur.execute(query)
    title = "level "+str(cur.fetchone()[0])
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in(), title=title)


@app.route('/word/<word_id>')
def render_entry(word_id):  # # Takes the user to a page for details on a word
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT Maori, English, Category, Definition, Level, Owner " \
            "FROM words " \
            "Where PK = " + word_id
    cur.execute(query)
    data = list(cur.fetchone())
    query = "SELECT Category " \
            "FROM Categories " \
            "Where PK = " + str(data[2])
    cur.execute(query)
    data[2] = cur.fetchone()[0]
    query = "SELECT level " \
            "FROM levels " \
            "Where PK = " + str(data[4])
    cur.execute(query)
    data[4] = cur.fetchone()[0]
    con.close()
    return render_template('entry.html', passed_data=data, logged_in=is_logged_in())


if __name__ == '__main__':
    app.run()
