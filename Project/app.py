from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    # Create Books
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

     # Create Authors
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Authors (
            Author_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            First_Name TEXT,
            Last_Name TEXT,
            Birthdate TEXT,
            Biography TEXT
        )
    ''')

    # Junction table Books_and_Authors
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Books_and_Authors (
            ISBN TEXT,
            Author_ID INTEGER,
            FOREIGN KEY (ISBN) REFERENCES Books (ISBN),
            FOREIGN KEY (Author_ID) REFERENCES Authors (Author_ID)
        )
    ''')

    # Copies Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Copies (
            Barcode INTEGER PRIMARY KEY AUTOINCREMENT,
            ISBN TEXT,
            Status TEXT,
            Shelf TEXT,
            Language TEXT,
            Page_Count INTEGER,
            Date_Added TEXT,
            FOREIGN KEY (ISBN) REFERENCES Books (ISBN)
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
    conn = get_db_connection()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        date_pub = request.form['date_pub']
        publisher = request.form['publisher']
        genre = request.form['genre']
        description = request.form['description']
        author_id = request.form['author_id']

        #conn = get_db_connection()

        # Insert book
        conn.execute('''
            INSERT INTO Books (ISBN, Title, Date_Pub, Publisher, Genre, Description)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, date_pub, publisher, genre, description))

        # Link book to author
        conn.execute('''
            INSERT INTO Books_and_Authors (ISBN, Author_ID)
            VALUES (?, ?)
        ''', (isbn, author_id))

        # Generate Barcode
        #count = conn.execute('SELECT COUNT(*) FROM Copies').fetchone()[0]
        #barcode = count + 1

        # Insert copy (AUTOINCREMENT handles Barcode)
        conn.execute('''
            INSERT INTO Copies (ISBN, Status, Shelf, Language, Page_Count, Date_Added)
            VALUES (?, ?, ?, ?, ?, DATE('now'))
        ''', (isbn, 'Available', 'Unknown', 'English', 0))

        conn.commit()
        conn.close()

        return redirect('/')

    # GET request → fetch authors
    authors = conn.execute('SELECT * FROM Authors').fetchall()
    conn.close()

    return render_template('add_book.html', authors=authors)


@app.route('/add_author', methods=('GET', 'POST'))
def add_author():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        birthdate = request.form['birthdate']
        bio = request.form['biography']

        conn = get_db_connection()

        # Generate Author_ID
        #count = conn.execute('SELECT COUNT(*) FROM Authors').fetchone()[0]
        #author_id = count + 1

        cursor = conn.execute('''
            INSERT INTO Authors (First_Name, Last_Name, Birthdate, Biography)
            VALUES (?, ?, ?, ?)
        ''', (first, last, birthdate, bio))

        author_id = cursor.lastrowid
        print("Inserted ID:", cursor.lastrowid)    

        conn.commit()
        conn.close()

        return redirect('/')


    return render_template('add_author.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)