-- -----------------------------
-- create School_Library_New database
-- -----------------------------
create database IF NOT EXISTS School_Library_New;
use School_Library_New;

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
    ON DELETE CASCADE
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
    ON DELETE CASCADE
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
  Return_Date date DEFAULT NULL,
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

CREATE INDEX idx_rental_date ON Rental(Rental_Date);
CREATE INDEX idx_return_date ON Rental(Return_Date);
CREATE INDEX idx_title ON Book(Title);
CREATE INDEX idx_author ON Author(First_Name,Last_Name);
CREATE INDEX idx_available_copies ON School_Books(Available_Copies);
CREATE UNIQUE INDEX idx_genre ON Category(Genre);
CREATE UNIQUE INDEX idx_username ON User(Username);




DELIMITER $$
create trigger reservation_limit 
before insert on book_reservation
for each row
begin
     declare reservation int UNSIGNED;
     set reservation = (
          select count(*) 
          from book_reservation
          where user_id = new.user_id 
               and datediff(curdate(),reservation_date)<7
     );
     if (new.user_id in (SELECT User_ID FROM User WHERE Is_Teacher = TRUE) and reservation>=1) or (new.user_id in (SELECT User_ID FROM User WHERE Is_Teacher = False) and reservation>=2) then
     signal sqlstate '45000' set message_text = 'You have exceeded weekly reservation limit';
     end if;
end $$
DELIMITER ;

DELIMITER $$
create trigger rental_limit 
before insert on rental
for each row
begin
     declare rents int UNSIGNED;
     set rents = (
          select count(*) 
          from rental
          where user_id = new.user_id 
               and datediff(curdate(),rental_date)<7
     );
     if (new.user_id in (SELECT User_ID FROM User WHERE Is_Teacher = TRUE) and rents>=1) or (new.user_id in (SELECT User_ID FROM User WHERE Is_Teacher = False) and rents>=2) then
     signal sqlstate '45000' set message_text = 'User has exceeded weekly rental limit';
     end if;
end $$
DELIMITER ;

DELIMITER $$
create trigger duplicate_reservations 
before insert on book_reservation
for each row
begin
     if exists(
          select * 
          from rental 
          where user_id = new.user_id 
          and isbn = new.isbn 
          and return_date is null) 
          then
          signal sqlstate '45000'
          set message_text = 'You cannot reserve a book that you have already rented and not returned';
     end if;
end $$
DELIMITER ;

DELIMITER $$
create trigger prevent_reservation_due_to_delay 
before insert on book_reservation
for each row
begin
     if exists 
          (select * from rental
               where user_id = new.user_id
               and datediff(curdate(),rental_date)>7
               and return_date is null
          ) 
          then
          signal sqlstate '45000'
          set message_text = 'You are not eligible to reserve a book because you have an existing rental that is overdue';
     end if;
end $$
DELIMITER ;


DELIMITER $$
create trigger prevent_rental_due_to_delay 
before insert on Rental
for each row
begin
     if exists 
          (select * from rental
               where user_id = new.user_id
               and datediff(curdate(),rental_date)>7
               and return_date is null
          ) 
          then
          signal sqlstate '45000'
          set message_text = 'User is not eligible to rent a book because he has an existing rental that is overdue';
     end if;
end $$
DELIMITER ;



DELIMITER //
CREATE TRIGGER trg_check_email
BEFORE INSERT ON Pending_Registrations
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Email = NEW.Email) 
    OR EXISTS (SELECT * FROM Administrator WHERE Email = NEW.Email) 
    OR EXISTS (SELECT * FROM User WHERE Email = NEW.Email) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email already in use';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_email_operator
BEFORE INSERT ON Operator_Registration
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Email = NEW.Email) 
    OR EXISTS (SELECT * FROM Administrator WHERE Email = NEW.Email) 
    OR EXISTS (SELECT * FROM User WHERE Email = NEW.Email) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email already in use';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_email_administrator
BEFORE INSERT ON Administrator
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Email = NEW.Email) 
    OR EXISTS (SELECT * FROM Administrator WHERE Email = NEW.Email AND Administrator_ID != NEW.Administrator_ID) 
    OR EXISTS (SELECT * FROM User WHERE Email = NEW.Email) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Email already in use';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_username
BEFORE INSERT ON Pending_Registrations
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM Administrator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM User WHERE Username = NEW.Username) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Username already in use';
    END IF;
END//
DELIMITER ;

DELIMITER //
CREATE TRIGGER trg_check_username_operator
BEFORE INSERT ON Operator_Registration
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM Administrator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM User WHERE Username = NEW.Username) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Username already in use';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_username_operator2
BEFORE INSERT ON Operator
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM Administrator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM User WHERE Username = NEW.Username) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Username already in use';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_username_administrator
BEFORE INSERT ON Administrator
FOR EACH ROW
BEGIN
    IF EXISTS (SELECT * FROM Operator WHERE Username = NEW.Username) 
    OR EXISTS (SELECT * FROM Administrator WHERE Username = NEW.Username AND Administrator_ID != NEW.Administrator_ID) 
    OR EXISTS (SELECT * FROM User WHERE Username = NEW.Username) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Username already in use';
    END IF;
END//
DELIMITER ;



DELIMITER //
CREATE TRIGGER trg_check_email_format
BEFORE INSERT ON User
FOR EACH ROW
BEGIN
    IF NEW.Email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid email format.';
    END IF;
END//
DELIMITER ;

DELIMITER //

CREATE TRIGGER before_reservation_trigger
BEFORE INSERT ON Book_Reservation
FOR EACH ROW
BEGIN
    DECLARE school_name1 VARCHAR(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    DECLARE count INT;
    
    -- Get the school name of the user
    SELECT School_Name INTO school_name1 FROM User WHERE User_ID = NEW.User_ID;
    
    -- Check if the book belongs to the user's school library
    SELECT COUNT(*) INTO count FROM School_Books WHERE School_Name = school_name1 AND ISBN = NEW.ISBN;
    
    -- If the book doesn't belong to the user's school library, raise an error
    IF count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Reservation failed. Book does not belong to the user''s school library.';
    END IF;
END //

DELIMITER ;


DELIMITER //

CREATE TRIGGER prevent_operator_duplicate
BEFORE INSERT ON School
FOR EACH ROW
BEGIN
    DECLARE operator_count INT;

    SELECT COUNT(*) INTO operator_count
    FROM School
    WHERE Operator_ID = NEW.Operator_ID;

    IF operator_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'An operator cannot be assigned to more than one school.';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER prevent_operator_duplicate_on_update
BEFORE UPDATE ON School
FOR EACH ROW
BEGIN
    DECLARE operator_count INT;

    -- Check if the operator already exists in another school
    SELECT COUNT(*) INTO operator_count
    FROM School
    WHERE Operator_ID = NEW.Operator_ID AND NEW.Name <> Name;

    -- Raise an error if the operator already exists in another school
    IF operator_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'An operator cannot be assigned to more than one school.';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_email_format_school
BEFORE UPDATE ON School
FOR EACH ROW
BEGIN
    IF NEW.Email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid email format.';
    END IF;
END//
DELIMITER ;


DELIMITER //
CREATE TRIGGER trg_check_email_format_school_add
BEFORE INSERT ON School
FOR EACH ROW
BEGIN
    IF NEW.Email NOT REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$' THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Invalid email format.';
    END IF;
END//
DELIMITER ;


DELIMITER //

CREATE PROCEDURE rental_return(
  IN isbn_param CHAR(13) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  IN user_id_param INT UNSIGNED
)
BEGIN
    update rental
    set return_date = curdate()
    where isbn = isbn_param 
    and user_id = user_id_param
    and Return_Date is NULL;
END//

DELIMITER ;


DELIMITER //
CREATE PROCEDURE create_rental(
  IN isbn_param CHAR(13),
  IN user_username1 VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN
    DECLARE user_id1 INT;

    -- Check if the operator already exists in another school
    SELECT u.user_ID INTO user_id1 
    FROM User u
    WHERE u.Username = user_username1;

    INSERT INTO Rental(ISBN, User_ID, Rental_Date)
    VALUES (isbn_param, user_id1, CURDATE());
END//

DELIMITER ;






DELIMITER //
CREATE PROCEDURE accept_pending_registrations(
    IN user_username VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN 
    DECLARE Username1 varchar(45);
    DECLARE Password1 varchar(45);
    DECLARE First_Name1 varchar(45);
    DECLARE Last_Name1 varchar(45);
    DECLARE Email1 varchar(45);
    DECLARE School_Name1 varchar(100);
    DECLARE Date_Of_Birth1 date;
    DECLARE Is_Teacher1 BOOLEAN;

    DECLARE cur CURSOR FOR SELECT Username, Password, First_Name, Last_Name, Email, School_Name,Date_Of_Birth, Is_Teacher
    FROM Pending_Registrations p
    WHERE p.username = user_username;
    
    OPEN cur;

    FETCH cur INTO Username1, Password1, First_Name1, Last_Name1, Email1, School_Name1,Date_Of_Birth1, Is_Teacher1;

    INSERT INTO user(Username,Password,First_Name,Last_Name,Email,School_Name,Date_Of_Birth,Is_Teacher) values(Username1,Password1,First_Name1,Last_Name1,Email1,School_Name1,Date_Of_Birth1,Is_Teacher1);
    DELETE FROM Pending_Registrations where username = user_username ;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE accept_operator_registrations(
    IN operator_username VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN 
    DECLARE Username1 VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    DECLARE Password1 varchar(45);
    DECLARE First_Name1 varchar(45);
    DECLARE Last_Name1 varchar(45);
    DECLARE Email1 varchar(45);
    DECLARE School_Name1 varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
    DECLARE New_Operator_ID INT UNSIGNED;


    DECLARE cur CURSOR FOR SELECT Username, Password, First_Name, Last_Name, Email, School_Name
    FROM Operator_Registration r
    WHERE r.username = operator_username;
    
    OPEN cur;

    FETCH cur INTO Username1, Password1, First_Name1, Last_Name1, Email1, School_Name1;


    INSERT INTO Operator(Username,Password,First_Name,Last_Name,Email) values(Username1,Password1,First_Name1,Last_Name1,Email1);
    SET New_Operator_ID = LAST_INSERT_ID(); -- Get the ID of the newly inserted operator

    UPDATE School
    SET Operator_ID = New_Operator_ID
    WHERE Name = School_Name1;

    DELETE FROM Operator_Registration where username = operator_username;

END //
DELIMITER ;





DELIMITER //

CREATE PROCEDURE delete_operator(
    IN operator1 INT UNSIGNED
)
BEGIN
    -- Set Operator_ID to NULL in School table for corresponding operator
    UPDATE School
    SET Operator_ID = NULL
    WHERE Operator_ID = operator1;
    
    -- Delete operator tuple from Operator table
    DELETE FROM Operator
    WHERE Operator_ID = operator1;
END //

DELIMITER ;






