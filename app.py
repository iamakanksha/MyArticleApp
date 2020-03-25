from flask import Flask, render_template, flash, redirect, url_for, session, logging, request
#from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps
app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'myflaskapp'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
# init MYSQL
mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about_us():
    return render_template('about_us.html')

@app.route('/articles')
def articles():
    cur = mysql.connection.cursor()
    # Get articles
    result = cur.execute("SELECT * FROM articles")
    articles = cur.fetchall()
    if result > 0:
        return render_template('articles.html', articles=articles)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg)
    # Close connection
    cur.close()

@app.route('/article/<string:id>/')
def article(id):
    cur = mysql.connection.cursor()
    # Get articles
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = cur.fetchone()
    return render_template('article.html', article= article)

# Register Form Class
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    emailid = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

#registration
@app.route('/register', methods= ['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        emailid = form.emailid.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        #cursor and creating statement
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name,emailid,username,password) VALUES(%s,%s,%s,%s)",
        (name, emailid, username, password))
        mysql.connection.commit()
        cur.close()
        flash('You are now registered and you can now log in!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form = form)

#login
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_given = request.form['password']

        cur = mysql.connection.cursor()

        result = cur.execute("SELECT * FROM users where username = %s", [username])

        if result>0:
            data = cur.fetchone()
            password_db = data['password']

            if sha256_crypt.verify(password_given,password_db):
                app.logger.info("PASSWORD MATCHED!")
                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in! Welcome to your dashboard', 'success')
                return redirect(url_for('dashboard'))
            else:
                app.logger.info("PASSWORD NOT MATCHED!")
                error = 'Incorrect password!'
                return render_template('login.html', error = error)
        
        else:
            #app.logger.info("NO USER!")
            error = 'No user found for this username!'
            return render_template('login.html', error = error)

    return render_template('login.html')

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

#dashboard available after logging in 
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE author = %s", [session['username']])
    articles = cur.fetchall()
    if result > 0:
        return render_template('dashboard.html', articles = articles)
    else:
        msg = 'No articles found!'
        return render_template('dashboard.html', msg = msg)
    cur.close()

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=250)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/add_article', methods = ['POST', 'GET'])
@is_logged_in
def addArticle():
    form = ArticleForm(request.form)    
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data
        author = session['username']
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO articles(title,body,author) VALUES(%s,%s,%s)",
        (title, body, author))
        mysql.connection.commit()
        cur.close()
        flash('Your article has been added!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('addArticle.html', form = form)

#logout 
@app.route('/logout') 
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('login'))

# Edit Article
@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    # Create cursor
    cur = mysql.connection.cursor()
    # Get article by id
    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])
    article = cur.fetchone()
    cur.close()
    # Get form
    form = ArticleForm(request.form)
    # Populate article form fields
    form.title.data = article['title']
    form.body.data = article['body']
    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']
        # Create Cursor
        cur = mysql.connection.cursor()
        app.logger.info(title)
        cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))
        mysql.connection.commit()
        cur.close()
        flash('Article Updated', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form)

# Delete Article
@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):
    # Create cursor
    cur = mysql.connection.cursor()
    # Execute
    cur.execute("DELETE FROM articles WHERE id = %s", [id])
    # Commit to DB
    mysql.connection.commit()
    #Close connection
    cur.close()
    flash('Article Deleted', 'success')
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    #inorder to run sessions
    app.secret_key = "secret123"
    app.run(host='localhost', port='5000',debug=True)
