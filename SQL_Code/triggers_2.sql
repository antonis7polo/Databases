

--RESERVATION LIMIT TRIGGER--
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
     signal sqlstate '45000' set message_text = 'User has exceeded weekly reservation limit';
     end if;
end $$
DELIMITER ;

--RENTAL LIMIT TRIGGER--
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



--DUPLICATE RESERVATION TRIGGER--
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
          set message_text = 'Cannot reserve a book that user has already rented and not returned';
     end if;
end $$
DELIMITER ;


--PREVENT OVERDUE RESERVATION TRIGGER--
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
          set message_text = 'User is not eligible to reserve a book because he has an existing rental that is overdue';
     end if;
end $$
DELIMITER ;

--UNIQUE EMAILS user--
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

--UNIQUE EMAILS operator--
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

--UNIQUE EMAILS administrator--
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



--UNIQUE USERNAME USER--
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

--UNIQUE USERNAME OPERATOR--
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

--UNIQUE USERNAME OPERATOR2--
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

--UNIQUE USERNAME ADMINISTRATOR--
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





--CHECK EMAIL FORMAT--
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



--DECREASE AVAILABLE COPIES--
DELIMITER //
create trigger decrease_available_copies 
after insert on rental
for each row
begin
     if new.return_date is null then
          update school_books b
          set b.available_copies = b.available_copies-1
          where b.isbn = new.isbn and b.school_name = (
               select u.school_name 
               from user u
               where u.user_id = new.user_id);
     end if;
end//
DELIMITER ;



--INCREASE AVAILABLE COPIES--
DELIMITER //
create trigger increase_available_copies after update on rental
for each row
begin
     if new.return_date is not null and old.return_date is null then
          update school_books b
          set b.available_copies = b.available_copies+1
          where b.isbn = new.isbn and b.school_name = (
               select u.school_name from user u
               where u.user_id = new.user_id);
     end if;
end// 
DELIMITER ;



---------------
DELIMITER //

CREATE PROCEDURE insert_reservations_to_rentals()
BEGIN
  DECLARE done INT DEFAULT FALSE;
  DECLARE reservation_id1 INT UNSIGNED;
  DECLARE isbn1 CHAR(13) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
  DECLARE user_id1 INT UNSIGNED;
  DECLARE reservation_date1 DATE;
  DECLARE available_copies1 INT UNSIGNED;
  declare rents int UNSIGNED;

  DECLARE cur CURSOR FOR SELECT Reservation_ID, ISBN, User_ID, Reservation_Date FROM Book_Reservation
  WHERE Is_Rented = False
  ORDER BY Reservation_Date ASC;

  DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

  OPEN cur;


  
  read_loop: LOOP
    FETCH cur INTO reservation_id1, isbn1, user_id1, reservation_date1;
    IF done THEN
      LEAVE read_loop;
    END IF;


    select count(*) INTO rents
    from rental
    where user_id = user_id1
    and datediff(curdate(),rental_date)<7;

    IF (user_id1 in (SELECT User_ID FROM User WHERE Is_Teacher = TRUE) and rents>=1) or (user_id1 in (SELECT User_ID FROM User WHERE Is_Teacher = False) and rents>=2) then  
        ITERATE read_loop;
    END IF;

    
    SELECT sb.Available_Copies INTO available_copies1
    FROM School_Books sb
    JOIN User u ON u.School_Name = sb.School_Name
    JOIN School s ON s.Name = sb.School_Name
    WHERE sb.ISBN = isbn1 AND u.User_ID = user_id1 AND s.Name = u.School_Name;


    
    IF (available_copies1 = 0) THEN
        ITERATE read_loop;
    END IF;

    INSERT INTO Rental (ISBN, User_ID, Rental_Date, Return_Date) VALUES (isbn1, user_id1, CURDATE(), NULL);
    UPDATE  Book_Reservation 
    SET Is_Rented = True
    WHERE Reservation_ID = reservation_id1;
   

  END LOOP;
  CLOSE cur;
  
END//

DELIMITER ;



---------------------
DELIMITER //
CREATE TRIGGER trg_book_reservation_ins BEFORE INSERT ON book_reservation
FOR EACH ROW
BEGIN
    IF NOT EXISTS (SELECT * FROM User u 
                   JOIN school_books sb ON u.School_Name = sb.School_Name 
                   WHERE u.User_ID = NEW.User_ID AND sb.ISBN = NEW.ISBN) THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = "Cannot insert book_reservation record for a book not available in the user's school.";
    END IF;
END//
DELIMITER ;



--------------
DELIMITER //

CREATE PROCEDURE create_reservation(
  IN isbn_param CHAR(13),
  IN user_id_param INT UNSIGNED
)
BEGIN
    INSERT INTO Book_Reservation(ISBN, User_ID, Reservation_Date)
    VALUES (isbn_param, user_id_param, CURDATE());
END//

DELIMITER ;
--------------------
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
--------------------------

DELIMITER //
CREATE PROCEDURE create_rental(
  IN isbn_param CHAR(13),
  IN user_id_param INT UNSIGNED
)
BEGIN
    INSERT INTO Rental(ISBN, User_ID, Rental_Date)
    VALUES (isbn_param, user_id_param, CURDATE());
END//

DELIMITER ;

----------------------------------------------
DELIMITER //
CREATE EVENT delete_old_reservations
ON SCHEDULE EVERY 1 DAY
STARTS '2023-05-19 00:00:00'
ON COMPLETION PRESERVE
DO
  BEGIN
    DELETE FROM Book_Reservation
    WHERE reservation_date < DATE_SUB(NOW(), INTERVAL 1 WEEK);
END//
DELIMITER ;
-----------------------------------------------

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

-------------------------
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


----------

DELIMITER //
CREATE TRIGGER before_update_school
BEFORE UPDATE ON School
FOR EACH ROW
BEGIN
    IF (OLD.Operator_ID IS NOT NULL) AND (NEW.Operator_ID  IS NOT NULL)THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Operator already exists for this school';
    END IF;
END //
DELIMITER ;


----------------------
DELIMITER //

CREATE TRIGGER prevent_operator_duplicate
BEFORE INSERT ON School
FOR EACH ROW
BEGIN
    DECLARE operator_count INT;

    -- Check if the operator already exists in another school
    SELECT COUNT(*) INTO operator_count
    FROM School
    WHERE Operator_ID = NEW.Operator_ID;

    -- Raise an error if the operator already exists in another school
    IF operator_count > 0 THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'An operator cannot be assigned to more than one school.';
    END IF;
END//
DELIMITER ;


------------------
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

