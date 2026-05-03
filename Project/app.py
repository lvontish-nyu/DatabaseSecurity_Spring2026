from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

print("APP STARTING")
print(app.url_map)

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
            Status TEXT CHECK (Status IN ('Available', 'Checked Out', 'Lost', 'Maintenance', 'On Hold')),
            Shelf TEXT,
            Language TEXT,
            Page_Count INTEGER,
            Date_Added TEXT,
            Checkouts INTEGER DEFAULT 0,
            FOREIGN KEY (ISBN) REFERENCES Books (ISBN)
        )
    ''')

    # Popular Books View
    conn.execute('''
        CREATE VIEW IF NOT EXISTS PopularBooks AS
        SELECT 
            b.ISBN,
            b.Title,
            GROUP_CONCAT(a.First_Name || ' ' || a.Last_Name, ', ') AS Authors,
            cp.Total_Checkouts,
            cp.Available_Copies
        FROM Books b

        -- Aggregate copies FIRST
        JOIN (
            SELECT 
                ISBN,
                SUM(Checkouts) AS Total_Checkouts,
                SUM(CASE WHEN Status = 'Available' THEN 1 ELSE 0 END) AS Available_Copies
            FROM Copies
            GROUP BY ISBN
        ) cp ON b.ISBN = cp.ISBN

        LEFT JOIN Books_and_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.Author_ID = a.Author_ID

        WHERE cp.Available_Copies > 0

        GROUP BY b.ISBN;
    ''')

    # Book Catalogue View:
    conn.execute('''
        CREATE VIEW IF NOT EXISTS BookCatalog AS
        SELECT
            b.ISBN,
            b.Title,
            b.Genre,
            b.Publisher,

            GROUP_CONCAT(a.First_Name || ' ' || a.Last_Name, ', ') AS Authors,

            SUM(CASE WHEN c.Status = 'Available' THEN 1 ELSE 0 END) AS Available_Copies

        FROM Books b
        LEFT JOIN Copies c ON b.ISBN = c.ISBN
        LEFT JOIN Books_and_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.Author_ID = a.Author_ID

        GROUP BY b.ISBN;
    ''')

    # Members Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Members (
            Card_Number INTEGER PRIMARY KEY AUTOINCREMENT,
            First_Name TEXT NOT NULL,
            Last_Name TEXT NOT NULL,
            Email TEXT UNIQUE NOT NULL,
            Phone TEXT,
            Address TEXT,
            Membership_Date TEXT DEFAULT (DATE('now')),
            Active INTEGER DEFAULT 1 CHECK (Active IN (0,1))
        )
    ''')

    # Loans Table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS Loans (
            Loan_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            Barcode INTEGER,
            Card_Number INTEGER,
            Checkout_Date TEXT,
            Due_Date TEXT,
            Return_Date TEXT,
            Status TEXT CHECK (Status IN ('Available', 'Checked Out', 'Overdue', 'Returned', 'Lost')),
            FOREIGN KEY (Barcode) REFERENCES Copies(Barcode),
            FOREIGN KEY (Card_Number) REFERENCES Members(Card_Number)
        )
    ''')

    # Loan Details View
    conn.execute('''
        CREATE VIEW IF NOT EXISTS LoanDetails AS
        SELECT 
            l.Loan_ID,
            l.Barcode,
            l.Card_Number,
            l.Checkout_Date,
            l.Due_Date,
            l.Return_Date,
            l.Status AS Loan_Status,
            c.ISBN,
            b.Title,
            a.First_Name || ' ' || a.Last_Name AS Author,
            m.Email
        FROM Loans l
        JOIN Copies c ON l.Barcode = c.Barcode
        JOIN Books b ON c.ISBN = b.ISBN
        LEFT JOIN Books_and_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.Author_ID = a.Author_ID
        JOIN Members m ON l.Card_Number = m.Card_Number;
    ''')

    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = get_db_connection()

    popular_books = conn.execute("""
        SELECT * FROM PopularBooks
        ORDER BY Total_Checkouts DESC
        LIMIT 10
    """).fetchall()

    conn.close()

    return render_template('index.html', popular_books=popular_books)

@app.route('/librarian')
def librarian():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM Books').fetchall()
    conn.close()
    return render_template('librarian.html', books=books)    

@app.route('/member', methods=['GET', 'POST'])
def member():
    conn = get_db_connection()

    search = request.form.get('search') if request.method == 'POST' else None

    query = "SELECT * FROM BookCatalog WHERE 1=1"
    params = []

    if search:
        query += """
        AND (
            Title LIKE ?
            OR ISBN LIKE ?
            OR Genre LIKE ?
            OR Authors LIKE ?
        )
        """
        params.extend([f'%{search}%'] * 4)

    books = conn.execute(query, params).fetchall()
    conn.close()

    return render_template('member.html', books=books, search=search)

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

        # Check that book exists before adding to Books
        existing_book = conn.execute('SELECT * FROM Books WHERE ISBN = ?', (isbn,)).fetchone()
        if not existing_book:
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

        return redirect('/librarian')

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

        return redirect('/librarian')

    return render_template('add_author.html')

@app.route('/tables')
def show_tables():
    conn = get_db_connection()

    books = conn.execute('SELECT * FROM Books').fetchall()
    authors = conn.execute('SELECT * FROM Authors').fetchall()
    books_authors = conn.execute('SELECT * FROM Books_and_Authors').fetchall()
    copies = conn.execute('SELECT * FROM Copies').fetchall()

    conn.close()

    return render_template(
        'show_tables.html',
        books=books,
        authors=authors,
        books_authors=books_authors,
        copies=copies
    )

@app.route('/delete_copy', methods=('GET', 'POST'))
def delete_copy():
    conn = get_db_connection()

    if request.method == 'POST':
        barcode = request.form['barcode']
        # Check if copy exists
        copy = conn.execute('SELECT * FROM Copies WHERE Barcode = ?', (barcode,)).fetchone()
        if copy:
            conn.execute('DELETE FROM Copies WHERE Barcode = ?', (barcode,))
            conn.commit()
            message = f"Copy with Barcode {barcode} deleted."
        else:
            message = f"No copy found with Barcode {barcode}."
    else:
        message = None

    # Fetch all copies with book title and author
    copies = conn.execute('''
        SELECT 
            c.Barcode,
            c.ISBN,
            c.Status,
            c.Shelf,
            c.Language,
            c.Page_Count,
            c.Date_Added,
            b.Title,
            a.First_Name || ' ' || a.Last_Name AS Author
        FROM Copies c
        JOIN Books b ON c.ISBN = b.ISBN
        LEFT JOIN Books_and_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.Author_ID = a.Author_ID
        ORDER BY c.Barcode
    ''').fetchall()

    conn.close()
    return render_template('delete_copy.html', copies=copies, message=message)

@app.route('/add_member', methods=('GET', 'POST'))
def add_member():
    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        conn = get_db_connection()

        try:
            conn.execute('''
                INSERT INTO Members (First_Name, Last_Name, Email, Phone, Address)
                VALUES (?, ?, ?, ?, ?)
            ''', (first, last, email, phone, address))

            conn.commit()
            conn.close()

            return redirect('/member')

        except sqlite3.IntegrityError:
            # Check for duplicate email
            error = "A member with this email already exists."
            conn.close()
            return render_template('add_member.html', error=error)

    return render_template('add_member.html')

@app.route('/member-management', methods=('GET', 'POST'))
def manage_members():
    conn = get_db_connection()

    search = request.form.get('search') if request.method == 'POST' else None

    if search:
        members = conn.execute('''
            SELECT * FROM Members
            WHERE First_Name LIKE ?
               OR Last_Name LIKE ?
               OR Email LIKE ?
        ''', (f'%{search}%', f'%{search}%', f'%{search}%')).fetchall()
    else:
        members = conn.execute('SELECT * FROM Members').fetchall()

    conn.close()
    return render_template('member_management.html', members=members)

@app.route('/edit_member/<int:card_number>', methods=('GET', 'POST'))
def edit_member(card_number):
    conn = get_db_connection()

    member = conn.execute(
        'SELECT * FROM Members WHERE Card_Number = ?',
        (card_number,)
    ).fetchone()

    if request.method == 'POST':
        first = request.form['first_name']
        last = request.form['last_name']
        email = request.form['email']
        phone = request.form['phone']
        address = request.form['address']

        try:
            conn.execute('''
                UPDATE Members
                SET First_Name = ?, Last_Name = ?, Email = ?, Phone = ?, Address = ?
                WHERE Card_Number = ?
            ''', (first, last, email, phone, address, card_number))

            conn.commit()
            conn.close()
            return redirect('/member-management')

        except sqlite3.IntegrityError:
            error = "Email already exists."
            return render_template('edit_member.html', member=member, error=error)

    conn.close()
    return render_template('edit_member.html', member=member)


@app.route('/deactivate_member/<int:card_number>')
def deactivate_member(card_number):
    conn = get_db_connection()

    conn.execute('''
        UPDATE Members
        SET Active = 0
        WHERE Card_Number = ?
    ''', (card_number,))

    conn.commit()
    conn.close()

    return redirect('/member-management')


@app.route('/reactivate_member/<int:card_number>')
def reactivate_member(card_number):
    conn = get_db_connection()

    conn.execute('''
        UPDATE Members
        SET Active = 1
        WHERE Card_Number = ?
    ''', (card_number,))

    conn.commit()
    conn.close()

    return redirect('/member-management')



@app.route('/checkout_page/<int:barcode>')
def checkout_page(barcode):
    conn = get_db_connection()
    cur = conn.cursor()

    copy = cur.execute("""
        SELECT Barcode, ISBN, Status
        FROM Copies
        WHERE Barcode = ?
    """, (barcode,)).fetchone()

    conn.close()

    if not copy:
        return "Copy not found", 404

    return render_template("checkout.html", copy=copy)


@app.route('/checkout_confirm', methods=['POST'])
def checkout_confirm():
    barcode = request.form['barcode']
    card_number = request.form.get('card_number')
    email = request.form.get('email')

    conn = get_db_connection()
    cur = conn.cursor()

    # Resolve member - make sure they are active
    if card_number:
        cur.execute("""
            SELECT Card_Number FROM Members
            WHERE Card_Number = ? AND Active = 1
        """, (card_number,))
        member = cur.fetchone()

    elif email:
        cur.execute("""
            SELECT Card_Number FROM Members
            WHERE Email = ? AND Active = 1
        """, (email,))
        member = cur.fetchone()

    else:
        conn.close()
        return "Must provide card number or email", 400

    if not member:
        conn.close()
        return "Member not found", 404

    card_number = member["Card_Number"]

    # Check availability
    cur.execute("""
        SELECT Status FROM Copies WHERE Barcode = ?
    """, (barcode,))
    copy = cur.fetchone()

    if not copy:
        conn.close()
        return "Copy not found", 404

    if copy["Status"] != "Available":
        conn.close()
        return "Copy is not available", 400

    # Update copy with new checkout status
    cur.execute("""
        UPDATE Copies
        SET Status = 'Checked Out',
            Checkouts = Checkouts + 1
        WHERE Barcode = ?
    """, (barcode,))

    # Create loan record
    cur.execute("""
        INSERT INTO Loans (
            Barcode, Card_Number, Checkout_Date, Due_Date, Return_Date, Status
        )
        VALUES (
            ?, ?, DATE('now'), DATE('now', '+14 days'), NULL, 'Checked Out'
        )
    """, (barcode, card_number))

    conn.commit()
    conn.close()

    return redirect('/librarian')





def checkin_copy(conn, cur, barcode):
    cur.execute("""
        UPDATE Copies
        SET Status = 'Available'
        WHERE Barcode = ? AND Status = 'Checked Out'
    """, (barcode,))

    if cur.rowcount == 0:
        return "Checkin failed"

    cur.execute("""
        UPDATE Loans
        SET Return_Date = DATE('now'),
            Status = 'Returned'
        WHERE Barcode = ? AND Return_Date IS NULL
    """, (barcode,))

    return None


@app.route('/scan_copy', methods=['POST'])
def scan_copy():
    barcode = request.form['barcode']

    conn = get_db_connection()
    cur = conn.cursor()

    copy = cur.execute("""
        SELECT Status
        FROM Copies
        WHERE Barcode = ?
    """, (barcode,)).fetchone()

    if not copy:
        conn.close()
        return "Copy not found", 404

    status = copy["Status"]

    # If the copy is checked out, automatically check it in
    if status == "Checked Out":
        error = checkin_copy(conn, cur, barcode)

        if error:
            conn.close()
            return error, 400

        conn.commit()
        conn.close()
        return redirect('/librarian')

    # If the copy is available, redirect to the checkout page
    elif status == "Available":
        conn.close()
        return redirect(f'/checkout_page/{barcode}')

    else:
        conn.close()
        return f"Cannot process status: {status}", 400


@app.route('/loan_search', methods=['GET', 'POST'])
def loan_search():
    conn = get_db_connection()
    cur = conn.cursor()

    query = "SELECT * FROM LoanDetails WHERE 1=1"
    params = []

    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        barcode = request.form.get('barcode')
        isbn = request.form.get('isbn')
        status = request.form.get('status')
        card_number = request.form.get('card_number')
        email = request.form.get('email')

        if title:
            query += " AND Title LIKE ?"
            params.append(f"%{title}%")

        if author:
            query += " AND Author LIKE ?"
            params.append(f"%{author}%")

        if barcode:
            query += " AND Barcode = ?"
            params.append(barcode)

        if isbn:
            query += " AND ISBN = ?"
            params.append(isbn)

        if status:
            query += " AND Loan_Status = ?"
            params.append(status)

        if card_number:
            query += " AND Card_Number = ?"
            params.append(card_number)

        if email:
            query += " AND Email LIKE ?"
            params.append(f"%{email}%")

    loans = cur.execute(query, params).fetchall()

    conn.close()

    return render_template('loan_search.html', loans=loans)

@app.route('/mark_lost/<int:loan_id>', methods=['POST'])
def mark_lost(loan_id):
    conn = get_db_connection()
    cur = conn.cursor()

    # Get loan and barcode
    loan = cur.execute("""
        SELECT Loan_ID, Barcode, Status
        FROM Loans
        WHERE Loan_ID = ?
    """, (loan_id,)).fetchone()

    if not loan:
        conn.close()
        return "Loan not found", 404

    if loan["Status"] not in ("Checked Out", "Overdue"):
        conn.close()
        return "Cannot mark this loan as lost", 400

    barcode = loan["Barcode"]

    # Update Copies
    cur.execute("""
        UPDATE Copies
        SET Status = 'Lost'
        WHERE Barcode = ?
    """, (barcode,))

    # Update Loan
    cur.execute("""
        UPDATE Loans
        SET Status = 'Lost',
            Return_Date = DATE('now')
        WHERE Loan_ID = ?
    """, (loan_id,))

    conn.commit()
    conn.close()

    return redirect('/loan_search')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)