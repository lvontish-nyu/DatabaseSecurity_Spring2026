BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "Books" (
	"ISBN"	TEXT,
	"Title"	TEXT NOT NULL,
	"Date_Pub"	TEXT,
	"Publisher"	TEXT,
	"Genre"	TEXT,
	"Description"	TEXT,
	PRIMARY KEY("ISBN")
);
CREATE TABLE IF NOT EXISTS "Authors" (
	"Author_ID"	INTEGER,
	"First_Name"	TEXT,
	"Last_Name"	TEXT,
	"Birthdate"	TEXT,
	"Biography"	TEXT,
	PRIMARY KEY("Author_ID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Books_and_Authors" (
	"ISBN"	TEXT,
	"Author_ID"	INTEGER,
	FOREIGN KEY("Author_ID") REFERENCES "Authors"("Author_ID"),
	FOREIGN KEY("ISBN") REFERENCES "Books"("ISBN")
);
CREATE TABLE IF NOT EXISTS "Copies" (
	"Barcode"	INTEGER,
	"ISBN"	TEXT,
	"Status"	TEXT CHECK("Status" IN ('Available', 'Checked Out', 'Lost', 'Maintenance', 'On Hold')),
	"Shelf"	TEXT,
	"Language"	TEXT,
	"Page_Count"	INTEGER,
	"Date_Added"	TEXT,
	"Checkouts"	INTEGER DEFAULT 0,
	PRIMARY KEY("Barcode" AUTOINCREMENT),
	FOREIGN KEY("ISBN") REFERENCES "Books"("ISBN")
);
CREATE TABLE IF NOT EXISTS "Holds" (
	"Hold_ID"	INTEGER,
	"ISBN"	TEXT NOT NULL,
	"Card_Number"	INTEGER NOT NULL,
	"Hold_Date"	TEXT DEFAULT (DATE('now')),
	"Status"	TEXT DEFAULT 'Active' CHECK("Status" IN ('Active', 'Ready', 'Fulfilled', 'Cancelled')),
	"Loan_ID"	INTEGER,
	FOREIGN KEY("ISBN") REFERENCES "Books"("ISBN"),
	FOREIGN KEY("Card_Number") REFERENCES "Members"("Card_Number"),
	PRIMARY KEY("Hold_ID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Members" (
	"Card_Number"	INTEGER,
	"First_Name"	TEXT NOT NULL,
	"Last_Name"	TEXT NOT NULL,
	"Email"	TEXT NOT NULL UNIQUE,
	"Phone"	TEXT,
	"Address"	TEXT,
	"Membership_Date"	TEXT DEFAULT (DATE('now')),
	"Active"	INTEGER DEFAULT 1 CHECK("Active" IN (0, 1)),
	PRIMARY KEY("Card_Number" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Loans" (
	"Loan_ID"	INTEGER,
	"Barcode"	INTEGER,
	"Card_Number"	INTEGER,
	"Checkout_Date"	TEXT,
	"Due_Date"	TEXT,
	"Return_Date"	TEXT,
	"Status"	TEXT CHECK("Status" IN ('Available', 'Checked Out', 'Overdue', 'Returned', 'Lost')),
	FOREIGN KEY("Card_Number") REFERENCES "Members"("Card_Number"),
	FOREIGN KEY("Barcode") REFERENCES "Copies"("Barcode"),
	PRIMARY KEY("Loan_ID" AUTOINCREMENT)
);
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('1','The Fellowship of the Ring','0002-01-01','God','Fantasy','Book one in The Lord of the Rings');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('156','A Book of Books and Books','2026-05-01','KDP Baby!','Romantasy','Why are you reading this?');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('2','The Two Towers','0003-01-01','God','Fantasy','The second Lord of the Rings book');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('31337','The Cult of the Dead Cow','2026-05-01','.ooM','Hackers','A biography of the Cult of the Dead Cow.');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('3','The Return of the King','1952-01-01','God','Fantasy','The third book in the Lord of the Rings.');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('0-689-30994-5','Alanna: The First Adventure','1983-09-01','Atheneum','Fantasy','Alanna: The First Adventure is a fantasy novel by Tamora Pierce. Originally published in 1983, it is the first in a series of four books for young adults, The Song of the Lioness. Pierce originally drafted a single novel aimed at adults, but revised it to a series for young adults after being unable to find a publisher. Set in a time and place where girls are forbidden from becoming knights, the novel details the beginning of Alanna of Trebond''s training as a knight as she hides her gender from teachers and fellow pages.');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('0-679-45150-1','The Sparrow','1996-04-12','Villard','Speculative Fiction','The Sparrow (1996) is the first novel by author Mary Doria Russell. It won the Arthur C. Clarke Award, James Tiptree Jr. Award, Kurd-Laßwitz-Preis and the British Science Fiction Association Award. It was followed by a sequel, Children of God, in 1998. The title refers to Gospel of Matthew 10:29–31, which relates that not even a sparrow falls to the earth without God''s knowledge thereof.');
INSERT INTO "Books" ("ISBN","Title","Date_Pub","Publisher","Genre","Description") VALUES ('978-0-679-45635-3','Children of God','1998-03-24','Villard','Speculative Fiction','Father Emilio Sandoz is a Jesuit priest who has returned to Earth and is recovering from his experiences on the planet Rakhat (detailed in The Sparrow). He believes himself to be the only survivor of a disastrous mission to Rakhat that led to a massacre of a village of herbivore Runa people by their carnivorous Jana''ata rulers. Surely they won''t send this man back into hell?');
INSERT INTO "Authors" ("Author_ID","First_Name","Last_Name","Birthdate","Biography") VALUES (1,'Jolkein Rolkein Rolkein','Tolkein','0001-01-01','Tom Bombadil''s pen name');
INSERT INTO "Authors" ("Author_ID","First_Name","Last_Name","Birthdate","Biography") VALUES (2,'Joseph','Menn','2026-04-01','He writes some cool shit about hackers and the government.');
INSERT INTO "Authors" ("Author_ID","First_Name","Last_Name","Birthdate","Biography") VALUES (3,'Juneau','Lindsay','1967-04-20','Hacker, musician, and semi professional clown.');
INSERT INTO "Authors" ("Author_ID","First_Name","Last_Name","Birthdate","Biography") VALUES (4,'Fake','Name','1234-01-01','Not a fake person');
INSERT INTO "Authors" ("Author_ID","First_Name","Last_Name","Birthdate","Biography") VALUES (5,'Tamora','Pierce','1954-12-13','Tamora Pierce (born December 13, 1954) is an American writer of fantasy fiction for teenagers, known best for stories featuring young heroines. She made a name for herself with her first book series, The Song of the Lioness (1983–1988), which followed the main character Alanna through the trials and triumphs of training as a knight.');
INSERT INTO "Authors" ("Author_ID","First_Name","Last_Name","Birthdate","Biography") VALUES (6,'Mary','Doria Russell','1950-08-19','Russell''s first two novels, The Sparrow and its sequel Children of God (1998)—sometimes called the Sparrow series[3] or Emilio Sandoz sequence[1]—(Random House Villard in 1996 and 1998) are speculative fiction novels focused on the religious and psychological implications of first contact with aliens. Both explore the problem of evil (theodicy) and how to reconcile a benevolent, omniscient, all-powerful deity with lives filled with undeserved suffering.');
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('1',1);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('156',3);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('156',4);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('2',1);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('31337',2);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('3',1);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('0-689-30994-5',5);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('0-679-45150-1',6);
INSERT INTO "Books_and_Authors" ("ISBN","Author_ID") VALUES ('978-0-679-45635-3',6);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (1,'1','Checked Out','Unknown','English',0,'2026-05-03',3);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (2,'1','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (3,'156','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (4,'2','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (5,'31337','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (6,'3','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (7,'0-689-30994-5','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (8,'0-679-45150-1','Available','Unknown','English',0,'2026-05-03',3);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (9,'978-0-679-45635-3','Available','Unknown','English',0,'2026-05-03',0);
INSERT INTO "Copies" ("Barcode","ISBN","Status","Shelf","Language","Page_Count","Date_Added","Checkouts") VALUES (10,'0-679-45150-1','Checked Out','Unknown','English',0,'2026-05-03',1);
INSERT INTO "Members" ("Card_Number","First_Name","Last_Name","Email","Phone","Address","Membership_Date","Active") VALUES (1,'Lindasy','Von Tish','lmv9443@nyu.edu','1(234)567-8910','127.0.0.1','2026-05-03',1);
INSERT INTO "Members" ("Card_Number","First_Name","Last_Name","Email","Phone","Address","Membership_Date","Active") VALUES (2,'Fake','Person','email@email.com','11111111','1234 Nowhere Ln','2026-05-03',1);
INSERT INTO "Members" ("Card_Number","First_Name","Last_Name","Email","Phone","Address","Membership_Date","Active") VALUES (3,'Johnathan','Doe VII','jdoe@jdoe.go','9999999999','1234 Doe Ave','2026-05-03',1);
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (1,1,1,'2026-05-03','2026-05-17','2026-05-03','Returned');
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (2,8,1,'2026-05-03','2026-05-17','2026-05-03','Returned');
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (3,10,3,'2026-05-03','2026-05-17',NULL,'Checked Out');
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (4,8,2,'2026-05-03','2026-05-17','2026-05-03','Returned');
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (5,1,3,'2026-05-03','2026-05-17','2026-05-03','Returned');
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (6,1,2,'2026-05-03','2026-05-17',NULL,'Checked Out');
INSERT INTO "Loans" ("Loan_ID","Barcode","Card_Number","Checkout_Date","Due_Date","Return_Date","Status") VALUES (7,8,3,'2026-05-03','2026-05-17','2026-05-03','Returned');
CREATE TRIGGER increment_checkouts
        AFTER UPDATE OF Status ON Copies
        WHEN NEW.Status = 'Checked Out' AND OLD.Status = 'Available'
        BEGIN
            UPDATE Copies
            SET Checkouts = Checkouts + 1
            WHERE Barcode = NEW.Barcode;
        END;
CREATE VIEW PopularBooks AS
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
CREATE VIEW BookCatalog AS
        SELECT
            b.ISBN,
            b.Title,
            b.Genre,
            b.Publisher,

            GROUP_CONCAT(a.First_Name || ' ' || a.Last_Name, ', ') AS Authors,
            COALESCE(SUM(CASE WHEN c.Status = 'Available' THEN 1 ELSE 0 END), 0) AS Available_Copies,
            COALESCE(SUM(CASE WHEN c.Status != 'Lost' THEN 1 ELSE 0 END), 0) AS Non_Lost_Copies,
            COALESCE(h.Hold_Count, 0) AS Hold_Count

        FROM Books b
        LEFT JOIN Copies c ON b.ISBN = c.ISBN
        LEFT JOIN Books_and_Authors ba ON b.ISBN = ba.ISBN
        LEFT JOIN Authors a ON ba.Author_ID = a.Author_ID

        -- Hold logic
        LEFT JOIN (
            SELECT 
                ISBN,
                COUNT(*) AS Hold_Count
            FROM Holds
            WHERE Status = 'Active'
            GROUP BY ISBN
        ) h ON b.ISBN = h.ISBN

        GROUP BY b.ISBN
        HAVING Non_Lost_Copies > 0;
CREATE VIEW LoanDetails AS
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
COMMIT;
