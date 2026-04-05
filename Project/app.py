from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Books (
            ISBN TEXT PRIMARY KEY,
            Title TEXT NOT NULL,
            Date_Pub TEXT,
            Publisher TEXT,
            Genre TEXT,
            Description TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM Books').fetchall()
    conn.close()
    return render_template('index.html', books=books)

@app.route('/add', methods=('GET', 'POST'))
def add_book():
    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        date_pub = request.form['date_pub']
        publisher = request.form['publisher']
        genre = request.form['genre']
        description = request.form['description']

        conn = get_db_connection()
        conn.execute('''
            INSERT INTO Books (ISBN, Title, Date_Pub, Publisher, Genre, Description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, date_pub, publisher, genre, description))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('add_book.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)