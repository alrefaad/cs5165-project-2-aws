from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, 'users.db')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')


@app.route('/')
def index():
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    email = request.form['email']
    address = request.form['address']

    file = request.files['file']
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)

    file.save(filepath)

    with open(filepath, 'r') as f:
        text = f.read()
        wordcount = len(text.split())

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('''
        INSERT INTO users
        (username, password, email, firstname, lastname, address,
         filename, filepath, wordcount)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        username,
        password,
        email,
        firstname,
        lastname,
        address,
        filename,
        filepath,
        wordcount
    ))

    conn.commit()
    conn.close()

    return redirect(url_for('profile', username=username))


@app.route('/profile/<username>')
def profile(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()

    conn.close()

    if user is None:
        return "User not found"

    return render_template('profile.html', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()
        conn.close()

        if user:
            return redirect(url_for('profile', username=username))

        return "Invalid username or password"

    return render_template('login.html')


@app.route('/download/<username>')
def download(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(
        "SELECT filepath, filename FROM users WHERE username=?",
        (username,)
    )

    file = c.fetchone()
    conn.close()

    if file is None:
        return "File not found"

    return send_file(file[0], as_attachment=True, download_name=file[1])


if __name__ == '__main__':
    app.run(debug=True)
