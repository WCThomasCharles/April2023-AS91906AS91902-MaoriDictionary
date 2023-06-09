
# ---------- Imports ----------
from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt
from datetime import datetime

# ---------- Variables ----------
DATABASE = "C:/Users/garet/OneDrive/Desktop/Thom/Programming/" \
           "GitHub Projects/April2023-AS91906AS91902-MaoriDictionary/dictionary.db"
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = "y4nm1e1w4cz3r3a"


# ---------- Functions ----------
# These functions are called by app functions and contain common task
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


# ---------- App Functions ----------
# All app functions render a template, or reroute to another app route that renders a template
# All app routes pass the 'logged_in' bool onto the template

@app.route('/')
def render_home():  # Takes the user to the home page
    return render_template('home.html', logged_in=is_logged_in())


@app.route('/login', methods=['POST', 'GET'])
def render_login():  # takes the user to the login page
    if is_logged_in():  # if the user is already logged in, redirects home
        return redirect("/")

    if request.method == 'POST':  # checks if the function is being called in association with a form being submitted
        # requests the users email and password from the form
        email = request.form['email'].strip().lower()
        password = request.form['password'].strip()

        # establishes query and creates a connection to the database
        # query collects the primary key, name, hashed password, and admin status \
        # associated with a variable email \
        # from the users table
        query = """SELECT PK, Firstname, Hashpass, Admin FROM users WHERE email = ?"""
        con = create_connection(DATABASE)
        cur = con.cursor()

        # collects the user data from the database according to the query using the forms email
        cur.execute(query, (email, ))
        user_data = cur.fetchall()[0]
        con.close()

        # trys to define variables using the data collected from the query
        try:
            user_id = user_data[0]
            first_name = user_data[1]
            hashpass = user_data[2]
            admin = user_data[3]
        except IndexError:  # if this try detects an IndexError
            # reroutes back to the login page and returns an error
            print("dataError")
            return redirect("/login?error=Invalid+username+or+password")

        # checks if the password entered fails to match the hashed password logged
        if not bcrypt.check_password_hash(hashpass, password):
            # reroutes back to the login page and returns an error
            print("passwordError")
            return redirect(request.referrer + "?error=Invalid+username+or+password")

        # if all checks are passed, creates a session using the users details
        session['email'] = email
        session['userid'] = user_id
        session['firstname'] = first_name
        session['admin'] = admin
        return redirect('/')  # redirects home
    return render_template('login.html', logged_in=is_logged_in())


@app.route('/logout')
def logout():  # logs the user out
    [session.pop(key) for key in list(session.keys())]  # removes each session element
    return redirect('/?message=See+you+next+time!')  # redirects home


@app.route('/signup', methods=['POST', 'GET'])
def render_signup():  # takes the user to the signup page and gathers their signup info
    if is_logged_in():  # if the user is already logged in, redirects home
        return redirect("/")
    if request.method == 'POST':  # checks if the function is being called in association with a form being submitted

        # puts data from the form into variables
        first_name = request.form.get('Firstname').title().strip()
        last_name = request.form.get('Lastname').title().strip()
        email = request.form.get('email').lower().strip()
        password = request.form.get('password')
        password2 = request.form.get('password2')
        admin = request.form.get('admin')

        # checks if the second password fails to match the first or if the password is too short
        if password != password2:
            return redirect("/signup?error=Passwords+do+not+match")  # redirects home
        if len(password) < 8:
            return redirect("/signup?error=Password+must+be+at+least+8+characters")  # redirects home

        # hashes the password
        hashed_password = bcrypt.generate_password_hash(password)

        # creates a connection the database and establishes a query
        con = create_connection(DATABASE)
        query = "INSERT INTO users (Firstname, Lastname, Email, Hashpass, Admin) VALUES (?, ?, ?, ?, ?)"
        cur = con.cursor()

        # trys to execute the query
        try:
            cur.execute(query, (first_name, last_name, email, hashed_password, admin))
        except sqlite3.IntegrityError:  # if it fails due to the email being a dupe redirects home
            con.close()
            return redirect("/signup?error=Email+is+already+used")

        con.commit()
        con.close()
        return redirect('/login')  # redirects to the login page

    return render_template("signup.html", logged_in=is_logged_in())


@app.route('/admin')
def render_admin():  # takes the user to the admin page
    if not is_logged_in() or not session.get('admin'):  # if the user is not logged in redirects them to the home page
        return redirect('/')

    # creates a connection to the database
    # establishes and executes three queries
    # query one collects primary key, and category from the categories table
    # query two collects the primary key, and level from the levels table
    # query two collects the maori, english, and pk from the words table
    query = "SELECT PK, Category " \
            "FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    categories = cur.fetchall()
    query = "SELECT PK, level " \
            "FROM levels"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    levels = cur.fetchall()
    query = "SELECT Maori, English, PK " \
            "FROM words"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    words = cur.fetchall()
    con.close()
    # passes on the collected data to the admin template
    return render_template('admin.html', categories=categories, levels=levels, words=words, logged_in=is_logged_in())


@app.route('/add/<table>/<column>', methods=['POST', 'GET'])
def add(table, column):  # adds a level or category
    if not is_logged_in():  # if the user isn't logged in redirects them home
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":

        # assigns the information in the form and session to variables
        name = request.form.get('name').title().strip()
        user = session.get("userid")

        # establishes a query and creates a connection to the database
        # query inserts a name, and user into a table
        con = create_connection(DATABASE)
        query = "INSERT INTO " + table + " (" + column + ", User) VALUES (?, ?)"
        cur = con.cursor()

        # executes the query using the form name and current session userid
        cur.execute(query, (name, user))
        con.commit()
        con.close()
        return redirect('/admin')  # redirects the user to the admin page


@app.route('/remove/<table>/', methods=['POST', 'GET'])
def remove(table):  # removes an entry
    if not is_logged_in():  # checks if the user is logged in and if not returns them to the home page
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":

        # checks that the user typed CONFIRM correctly
        if request.form.get('confirm') == "CONFIRM":

            # assigns the pk in the form to a variable
            pk = request.form.get('pk')

            # connects to the database and establishes a query
            # the query deletes an entry from a table
            con = create_connection(DATABASE)
            query = "DELETE FROM " + table + " WHERE PK = ?"
            cur = con.cursor()

            # executes the query in a table using the forms pk
            cur.execute(query, (pk, ))
            con.commit()
            con.close()

            # redirects the user to the admin page
            return redirect('/admin')
        else:
            # redirects the user to the admin page
            return redirect('/admin?message=Confirmation+failed.')


@app.route('/addword', methods=['POST', 'GET'])
def add_word():  # adds a word to the words table
    if not is_logged_in():  # checks if the user is logged in and if not redirects them to the home page
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":

        # assigns the data in the form to variables
        maori = request.form.get('maori').title().strip()
        english = request.form.get('english').title().strip()
        definition = request.form.get('definition').title().strip()
        category = request.form.get('category')
        level = request.form.get('level')
        user = session.get("userid")

        # establishes a query and connects to the database
        # query inserts a maori word, an english word, a category, a definition, a level, and an owner /
        # into the words table
        con = create_connection(DATABASE)
        query = "INSERT INTO words (Maori, English, Category, Definition, Level, Owner, DATE) " \
                "VALUES (?, ?, ?, ?, ?, ?, ?)"
        cur = con.cursor()

        # executes the query using form data
        cur.execute(query, (maori, english, category, definition, level, user,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        con.commit()
        con.close()
        return redirect('/admin')


@app.route('/edit/<pk>', methods=['POST', 'GET'])
def edit_word(pk):  # changes an entry in the word table
    if not is_logged_in():  # if the user isn't logged in and reroutes the home page
        return redirect('/?message=Need+to+be+logged+in.')
    if request.method == "POST":
        if request.form.get('confirm') == "CONFIRM":

            # assigns the data in the form to variables
            maori = str(request.form.get('maori').title().strip())
            english = str(request.form.get('english').title().strip())
            definition = str(request.form.get('definition').title().strip())
            category = str(request.form.get('category'))
            level = str(request.form.get('level'))

            # establishes a query and connects to the database
            # query updates a maori word, an english word, a category, a definition, a level /
            # in the words table
            con = create_connection(DATABASE)
            query = "UPDATE words SET Maori = ?, English = ?, " \
                    "Category = ?, Definition = ?, Level = ? " \
                    "WHERE PK = ?"
            cur = con.cursor()

            # executes the query using form data
            cur.execute(query, (maori, english, category, definition, level, pk))
            con.commit()
            con.close()
            return redirect('/admin')
        else:
            return redirect('/admin?message=Confirmation+failed.')


@app.route('/editer/<word>')
def render_editer(word):  # renders the editer
    if not is_logged_in() or not session.get('admin'):  # if the user isn't logged in and reroutes the home page
        return redirect('/')

    # establishes queries and connects to the database
    # query one gathers a primary key and category /
    # from the categories table
    # query two gathers a primary key and level /
    # from the levels table
    # query three gathers a maori word, an english word, a category, a definition, a level, and the primary key /
    # from the words table
    query = "SELECT PK, Category " \
            "FROM Categories"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    categories = cur.fetchall()
    query = "SELECT PK, level " \
            "FROM levels"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    levels = cur.fetchall()
    query = "SELECT Maori, English, Category, Level, Definition, PK " \
            "FROM words WHERE PK = "+word
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query)
    word_data = cur.fetchone()
    con.close()

    word_level = 1
    word_category = 1
    for level in levels:
        if word_data[3] == level[0]:
            word_level = level
    for category in categories:
        if str(word_data[2]) == str(category[0]):
            word_category = category
    levels.insert(0, levels.pop(levels.index(word_level)))
    categories.insert(0, categories.pop(categories.index(word_category)))
    return render_template('editer.html', categories=categories, levels=levels, word=word_data, logged_in=is_logged_in())


@app.route('/categories')
def render_categories():  # Takes the user to a list of links to categories

    # establishes a query and connects to the database
    # query gathers a primary key and category /
    # from the categories table
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
def render_category(category_id):  # Takes the user to a list of links to words

    # establishes a query and connects to the database
    # query gathers primary key, maori, and english /
    # from the words table by category
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where Category = " + category_id
    cur.execute(query)
    data = cur.fetchall()

    # establishes a second query
    # the query gathers the category associated with the category id /
    # from the categories table
    query = "SELECT Category " \
            "FROM Categories " \
            "Where PK = " + category_id
    cur.execute(query)
    title = str(cur.fetchone()[0])
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in(), title=title)


@app.route('/levels')
def render_levels():  # Takes the user to a list of links to levels

    # establishes a query and connects to the database
    # query gathers a primary key and level /
    # from the levels table
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

    # establishes a query and connects to the database
    # query gathers primary key, maori, and english /
    # from the words table by level
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT PK, Maori, English " \
            "FROM words " \
            "Where level = " + level_id
    cur.execute(query)
    data = cur.fetchall()

    # establishes a second query
    # the query gathers the level associated with the level id /
    # from the levels table
    query = "SELECT level " \
            "FROM levels " \
            "Where PK = " + level_id
    cur.execute(query)
    title = "level "+str(cur.fetchone()[0])
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in(), title=title)


@app.route('/word/<word_id>')
def render_entry(word_id):  # Takes the user to a page for details on a word

    # establishes a query and connects to the database
    # query gathers primary key, maori, english, definition, category, level, owner, and image /
    # from the words table
    con = create_connection(DATABASE)
    cur = con.cursor()
    query = "SELECT Maori, English, Category, Definition, Level, Owner, PK, Image " \
            "FROM words " \
            "Where PK = " + word_id
    cur.execute(query)

    # converts category id to it's associated category
    data = list(cur.fetchone())
    query = "SELECT Category " \
            "FROM Categories " \
            "Where PK = " + str(data[2])
    cur.execute(query)
    try:
        data[2] = cur.fetchone()[0]
    except TypeError:
        data[2] = "empty"

    # converts level id to it's associated level
    query = "SELECT level " \
            "FROM levels " \
            "Where PK = " + str(data[4])
    cur.execute(query)
    try:
        data[4] = cur.fetchone()[0]
    except TypeError:
        data[4] = "empty"
    con.close()
    return render_template('entry.html', passed_data=data, logged_in=is_logged_in())


@app.route('/search', methods=['GET', 'Post'])
def render_search():
    search = request.form['search']
    title = "Showing results for "+search
    query = "SELECT PK, Maori, English " \
            "FROM words WHERE Maori like ? OR English like ? OR Definition like ? "
    search = "%" + search + "%"
    con = create_connection(DATABASE)
    cur = con.cursor()
    cur.execute(query, (search, search, search))
    data = cur.fetchall()
    con.close()
    return render_template('href_list.html', passed_data=data, next_step="word", logged_in=is_logged_in(), title=title)


if __name__ == '__main__':
    app.run()
