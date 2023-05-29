-- -----------------------------
-- create School_Library database
-- -----------------------------
create database IF NOT EXISTS School_Library;
use School_Library;

CREATE TABLE IF NOT EXISTS Operator(
  Operator_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Username varchar(45) NOT NULL,
  Password varchar(45) NOT NULL,
  First_Name varchar(45) NOT NULL,
  Last_Name varchar(45) NOT NULL,
  Email varchar(45) NOT NULL,
  PRIMARY KEY(Operator_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



CREATE TABLE IF NOT EXISTS School (
  Name varchar(100) NOT NULL,
  Street varchar(45) NOT NULL,
  Street_Number int UNSIGNED NOT NULL,
  Postal_Code char(5) NOT NULL,
  City varchar(45) NOT NULL,
  Email varchar(45) NOT NULL,
  Phone varchar(45) NOT NULL,
  Principal_Full_Name varchar(45) NOT NULL,
  Operator_ID INT UNSIGNED,
  PRIMARY KEY (Name),
  CHECK (CHAR_LENGTH(Postal_Code) = 5),
  UNIQUE INDEX fk_School_Operator_idx (Operator_ID ASC),
  CONSTRAINT fk1_School_Operator
    FOREIGN KEY(Operator_ID) 
    REFERENCES Operator(Operator_ID) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Operator_Registration(
  Operator_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Username varchar(45) NOT NULL,
  Password varchar(45) NOT NULL,
  First_Name varchar(45) NOT NULL,
  Last_Name varchar(45) NOT NULL,
  Email varchar(45) NOT NULL,
  School_Name varchar(100) NOT NULL,
  PRIMARY KEY(Operator_ID),
  CONSTRAINT fk1_School_Operator_Registration
    FOREIGN KEY(School_Name) 
    REFERENCES School(Name) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS Pending_Registrations(
  Registration_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Username varchar(45) NOT NULL,
  Password varchar(45) NOT NULL,
  First_Name varchar(45) NOT NULL,
  Last_Name varchar(45) NOT NULL,
  Email varchar(45) NOT NULL,
  School_Name varchar(100) NOT NULL,
  Date_Of_Birth DATE NOT NULL,
  Is_Teacher BOOLEAN NOT NULL,
  PRIMARY KEY(Registration_ID),
  CONSTRAINT fk1_Pending_Registrations_School
    FOREIGN KEY(School_Name)
    REFERENCES School(Name)
    ON DELETE RESTRICT 
    ON UPDATE CASCADE
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
  
CREATE TABLE IF NOT EXISTS User(
  User_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Username varchar(45) NOT NULL,
  Password varchar(45) NOT NULL,
  First_Name varchar(45) NOT NULL,
  Last_Name varchar(45) NOT NULL,
  Email varchar(45) NOT NULL,
  School_Name varchar(100) NOT NULL,
  Date_Of_Birth DATE NOT NULL,
  Is_Teacher BOOLEAN NOT NULL,
  PRIMARY KEY(User_ID),
  CONSTRAINT fk1_User_School
    FOREIGN KEY(School_Name) 
    REFERENCES School(Name) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



CREATE TABLE IF NOT EXISTS Administrator(
  Administrator_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Username varchar(45) NOT NULL,
  Password varchar(45) NOT NULL,
  First_Name varchar(45) NOT NULL,
  Last_Name varchar(45) NOT NULL,
  Email varchar(45) NOT NULL,
  PRIMARY KEY (Administrator_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS Book(
  ISBN char(13) NOT NULL,
  Title varchar(100) NOT NULL,
  Number_Of_Pages int UNSIGNED NOT NULL,
  Publisher varchar(150) NOT NULL,
  Language varchar(45) NOT NULL DEFAULT 'Greek',
  Summary TEXT DEFAULT NULL,
  Image_URL varchar(1000) DEFAULT NULL,
  PRIMARY KEY (ISBN),
  CHECK(ISBN REGEXP '^[0-9]{13}$' and CHAR_LENGTH(ISBN) = 13)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Author(
  Author_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  First_Name varchar(45) NOT NULL,
  Last_Name varchar(45) NOT NULL,
  PRIMARY KEY(Author_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Book_Author(
  Author_ID INT UNSIGNED NOT NULL,
  ISBN char(13) NOT NULL,
  PRIMARY KEY(Author_ID,ISBN),
  CONSTRAINT fk1_Book_Author
    FOREIGN KEY(Author_ID) 
    REFERENCES Author(Author_ID) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Book_Author
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Keyword(
  Keyword_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Keyword varchar(45) NOT NULL,
  PRIMARY KEY(Keyword_ID)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Book_Keyword(
  Keyword_ID INT UNSIGNED NOT NULL,
  ISBN char(13) NOT NULL,
  PRIMARY KEY(Keyword_ID,ISBN),
  CONSTRAINT fk1_Book_Keyword
    FOREIGN KEY(Keyword_ID) 
    REFERENCES Keyword(Keyword_ID) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Book_Keyword
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Category(
  Category_Id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  Genre varchar(45) NOT NULL,
  PRIMARY KEY(Category_Id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Book_Category(
  Category_Id INT UNSIGNED NOT NULL,
  ISBN char(13) NOT NULL,
  PRIMARY KEY(Category_Id,ISBN),
  CONSTRAINT fk1_Book_Category
    FOREIGN KEY(Category_Id) 
    REFERENCES Category(Category_Id) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Book_Category
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Book_Reservation(
  Reservation_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ISBN char(13) NOT NULL,
  User_ID INT UNSIGNED NOT NULL,
  Reservation_Date date NOT NULL,
  Is_Rented BOOLEAN NOT NULL DEFAULT FALSE,
  PRIMARY KEY(Reservation_ID),
  CONSTRAINT fk1_Book_Reservation
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Book_Reservation
    FOREIGN KEY(User_ID) 
    REFERENCES User(User_ID) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Book_Review(
  Review_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ISBN char(13) NOT NULL,
  User_ID INT UNSIGNED NOT NULL,
  Review_Text varchar(1000) DEFAULT NULL,
  Review_Date date,
  Likert_Review enum('1','2','3','4','5') DEFAULT NULL,
  PRIMARY KEY(Review_ID),
  CONSTRAINT fk1_Book_Review
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Book_Review
    FOREIGN KEY(User_ID) 
    REFERENCES User(User_ID) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

CREATE TABLE IF NOT EXISTS Published_Book_Review(
  Published_Review_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ISBN char(13) NOT NULL,
  User_ID INT UNSIGNED NOT NULL,
  Review_Text varchar(1000) DEFAULT NULL,
  Review_Date date,
  Likert_Review enum('1','2','3','4','5') DEFAULT NULL,
  PRIMARY KEY(Published_Review_ID),
  CONSTRAINT fk1_Published_Book_Review
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Published_Book_Review
    FOREIGN KEY(User_ID) 
    REFERENCES User(User_ID) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;



CREATE TABLE IF NOT EXISTS Rental(
  Rental_ID INT UNSIGNED NOT NULL AUTO_INCREMENT,
  ISBN char(13) NOT NULL,
  User_ID INT UNSIGNED NOT NULL,
  Rental_Date date NOT NULL,
  Return_Date date,
  PRIMARY KEY(Rental_ID),
  CHECK (Return_Date >= Rental_Date),
  CONSTRAINT fk1_Book_Rental
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE RESTRICT
    ON UPDATE CASCADE,
  CONSTRAINT fk2_Book_Rental
    FOREIGN KEY(User_ID) 
    REFERENCES User(User_ID) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


CREATE TABLE IF NOT EXISTS School_Books(
  School_Name varchar(100) NOT NULL,
  ISBN char(13) NOT NULL,
  Available_Copies int UNSIGNED NOT NULL, 
  PRIMARY KEY(School_Name,ISBN),
  CONSTRAINT fk1_School_Books
    FOREIGN KEY(School_Name) 
    REFERENCES School(Name) 
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk2_School_Books
    FOREIGN KEY(ISBN) 
    REFERENCES Book(ISBN) 
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


