
--3.1.1
DELIMITER //
CREATE PROCEDURE get_rentals_by_school(IN start_time DATETIME, IN end_time DATETIME)
BEGIN
SELECT School.Name, COUNT(*) as Total_Rentals
FROM Rental
INNER JOIN User ON Rental.User_ID = User.User_ID
INNER JOIN School ON User.School_Name = School.Name
WHERE Rental.Rental_Date BETWEEN start_time AND end_time
GROUP BY School.Name;
END//


DELIMITER ;

--3.1.2 
DELIMITER //
CREATE PROCEDURE authors_categories (IN genre varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci)
BEGIN
SELECT DISTINCT Author.First_Name, Author.Last_Name
FROM Author
INNER JOIN Book_Author ON Author.Author_ID = Book_Author.Author_ID
INNER JOIN Book_Category ON Book_Author.ISBN = Book_Category.ISBN
INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id
WHERE Category.Genre = genre
COLLATE utf8mb4_general_ci;
END//

DELIMITER ;

DELIMITER //
CREATE PROCEDURE teachers_categories (IN genre varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci)
BEGIN
SELECT DISTINCT User.First_Name, User.Last_Name
FROM User
INNER JOIN Rental ON User.User_ID = Rental.User_ID
INNER JOIN Book_Category ON Rental.ISBN = Book_Category.ISBN
INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id
WHERE Category.Genre = genre
AND User.Is_Teacher = TRUE
AND Rental.Rental_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
COLLATE utf8mb4_general_ci;
END//

DELIMITER ;


--3.1.3
SELECT User.User_ID, User.First_Name, User.Last_Name, COUNT(*) AS Number_Of_Rentals
FROM User
INNER JOIN Rental ON User.User_ID = Rental.User_ID
WHERE User.Is_Teacher = TRUE
AND User.Date_Of_Birth > DATE_SUB(CURDATE(), INTERVAL 40 YEAR) 
GROUP BY User_ID
ORDER BY Number_Of_Rentals DESC
LIMIT 10;

--3.1.4
SELECT Author.Author_ID, Author.First_Name, Author.Last_Name
FROM Author
INNER JOIN Book_Author ON Author.Author_ID = Book_Author.Author_ID
LEFT JOIN Rental ON Book_Author.ISBN = Rental.ISBN
GROUP BY Author.Author_ID
HAVING COUNT(Rental.Rental_ID) = 0;

--3.1.5
SELECT o.Operator_ID, o.First_Name, o.Last_Name, COUNT(*) AS  Num_Rentals
FROM Operator o 
INNER JOIN School s ON o.Operator_ID = s.Operator_id
INNER JOIN User u ON s.Name = u.School_Name
INNER JOIN Rental r ON r.User_ID = u.User_ID
WHERE r.Rental_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
GROUP BY o.Operator_ID
HAVING Num_Rentals > 20 AND COUNT(*) = SOME(SELECT COUNT(*)
                                            FROM Operator o1    
                                            INNER JOIN School s1 ON o1.Operator_ID = s1.Operator_id
                                            INNER JOIN User u1 ON s1.Name = u1.School_Name
                                            INNER JOIN Rental r1 ON r1.User_ID = u1.User_ID
                                            WHERE r1.Rental_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
                                            AND o.Operator_ID <> o1.Operator_ID
                                            GROUP BY o1.Operator_ID)
ORDER BY Num_Rentals DESC;

--3.1.6
SELECT c1.Genre AS Category1, c2.Genre AS Category2, COUNT(*) AS Num_Rentals
FROM Rental r
INNER JOIN Book b ON b.ISBN = r.ISBN
INNER JOIN Book_Category bc1 ON bc1.ISBN = b.ISBN
INNER JOIN Category c1 ON c1.Category_ID = bc1.Category_ID
INNER JOIN Book_Category bc2 ON bc2.ISBN = b.ISBN
INNER JOIN Category c2 ON c2.Category_ID = bc2.Category_ID
WHERE c1.Category_ID < c2.Category_ID
GROUP BY c1.Category_ID, c2.Category_ID
HAVING COUNT(*) > 0
ORDER BY Num_Rentals DESC
LIMIT 3;

--3.1.7
SELECT a1.First_Name, a1.Last_Name, COUNT(*) AS Books_Written
FROM Author a1
INNER JOIN Book_Author ba1 ON a1.Author_ID = ba1.Author_ID
GROUP BY a1.Author_ID
HAVING COUNT(*) <= (SELECT COUNT(*)
                   FROM Author a2
                   INNER JOIN Book_Author ba2 ON a2.Author_ID = ba2.Author_ID
                   GROUP BY a2.Author_ID
                   ORDER BY COUNT(*) DESC
                   LIMIT 1) - 5;



--3.2.1

DELIMITER //

CREATE PROCEDURE operator_asks(IN in_title varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                                IN in_genre varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                                IN in_first_name varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                                IN in_last_name varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
                                IN in_available_copies int,
                                IN operator varchar(45)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci)
BEGIN
    SELECT DISTINCT Book.title, Author.First_Name, Author.Last_Name
    FROM Book 
    INNER JOIN School_Books ON Book.ISBN = School_Books.ISBN
    INNER JOIN School ON School.Name = School_Books.School_Name
    INNER JOIN Book_Author ON Book.ISBN = Book_Author.ISBN  
    INNER JOIN Author ON Author.Author_ID = Book_Author.Author_id
    INNER JOIN Book_Category ON Book_Category.ISBN = Book.ISBN
    INNER JOIN Category ON Book_Category.Category_ID = Category.Category_ID
    INNER JOIN Operator ON School.Operator_ID = Operator.Operator_ID
    WHERE Book.Title LIKE CONCAT('%', in_title, '%')
    AND Category.Genre LIKE CONCAT('%', in_genre, '%')
    AND Author.First_Name LIKE CONCAT('%', in_first_name, '%')
    AND Author.Last_Name LIKE CONCAT('%', in_last_name, '%')
    AND School_Books.Available_Copies >= in_available_copies
    AND Operator.username = operator
    ORDER BY Book.Title, Author.First_Name, Author.Last_Name
    COLLATE utf8mb4_general_ci;
END//

DELIMITER ;


--3.2.2
DELIMITER //
CREATE PROCEDURE overdue_rentals(IN first_name varchar(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
IN last_name varchar(45)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
IN delay_date int,
IN operator varchar(45)CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci)
BEGIN
SELECT DISTINCT u.Username, u.First_Name, u.Last_Name
FROM User u
INNER JOIN Rental r
ON u.user_id = r.user_id
INNER JOIN School s 
ON s.Name = u.School_Name
INNER JOIN Operator o
ON o.Operator_ID = s.Operator_ID
WHERE r.Return_Date IS NULL AND DATEDIFF(CURDATE(),r.Rental_Date)>7
AND u.First_Name LIKE CONCAT('%', first_name, '%')
AND u.Last_Name LIKE CONCAT('%', last_name, '%')
AND DATEDIFF(CURDATE(), r.Rental_Date) >= delay_date
AND o.Username = operator;
END//
DELIMITER ;


--3.2.3

DELIMITER //
CREATE PROCEDURE avg_reviews_per_user_and_category(
  IN user INT, 
  IN genre VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  IN operator int
)
BEGIN
  SELECT User.User_ID, Category.Genre, AVG(Book_Review.Likert_Review) AS avg_reviews_per_user_and_category
  FROM User 
  INNER JOIN Book_Review ON User.User_ID = Book_Review.User_ID 
  INNER JOIN Book_Category ON Book_Review.ISBN = Book_Category.ISBN 
  INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id 
  INNER JOIN School ON School.Name = User.School_Name
  WHERE User.User_ID = user 
  AND Category.Genre LIKE CONCAT('%', genre, '%')
  AND School.Operator_ID = operator
  GROUP BY User.User_ID, Category.Category_ID;
END //
DELIMITER ;


DELIMITER //
CREATE PROCEDURE avg_reviews_per_category(
  IN genre VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
  IN operator int
)
BEGIN
  SELECT User.User_ID,Category.Genre, AVG(Book_Review.Likert_Review) AS avg_reviews_per_user_and_category
  FROM User 
  INNER JOIN Book_Review ON User.User_ID = Book_Review.User_ID 
  INNER JOIN Book_Category ON Book_Review.ISBN = Book_Category.ISBN 
  INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id 
  INNER JOIN School ON School.Name = User.School_Name
  WHERE Category.Genre LIKE CONCAT('%', genre, '%')
  AND School.Operator_ID = operator
  GROUP BY User.User_ID, Category.Category_ID;
END //
DELIMITER ;





--3.3.1
DELIMITER //

CREATE PROCEDURE search_books(
  IN usrid INT, 
  IN search_title VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci, 
  IN search_category VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci, 
  IN search_author_first_name VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci, 
  IN search_author_last_name VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN
  SELECT DISTINCT b.ISBN, b.Title, sb.Available_Copies
  FROM User u
  INNER JOIN School_Books sb ON sb.School_Name = u.School_Name
  INNER JOIN Book b ON sb.ISBN = b.ISBN
  INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
  INNER JOIN Author a ON a.Author_ID = ba.Author_ID
  INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
  INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
  WHERE u.user_id = usrid
  AND b.Title LIKE CONCAT('%', search_title, '%')
  AND c.Genre LIKE CONCAT('%', search_category, '%')
  AND a.First_Name LIKE CONCAT('%', search_author_first_name, '%')
  AND a.Last_Name LIKE CONCAT('%', search_author_last_name, '%');
END//

DELIMITER ;




--3.3.2
DELIMITER //
CREATE PROCEDURE get_rented_books(
    IN username1 VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN
    SELECT DISTINCT Book.Title, Book.ISBN
    FROM Rental
    INNER JOIN Book ON Rental.ISBN = Book.ISBN
    INNER JOIN User ON Rental.User_ID = User.User_ID
    WHERE User.Username = username1;
END//
DELIMITER ;

--proc to get rentals by operator--
DELIMITER //
CREATE PROCEDURE get_not_overdue_rentals_by_operator(
    IN operator VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci,
    IN username1 VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN
SELECT u.user_id, u.Username, u.First_Name, u.Last_Name, r.Rental_ID, r.Rental_Date, r.return_date
FROM User u
INNER JOIN Rental r
ON u.user_id = r.user_id
INNER JOIN School s 
ON s.Name = u.School_Name
INNER JOIN operator o
ON o.Operator_ID = s.Operator_id
WHERE o.Username = operator
AND u.username LIKE CONCAT('%', username1, '%')
AND (DATEDIFF(CURDATE(), r.Rental_Date) <= 7 OR r.Return_Date IS NOT NULL);
END//
DELIMITER ;


--proc to get reservations by operator--
DELIMITER //
CREATE PROCEDURE get_reservations_by_operator(
    IN operator VARCHAR(45) CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci
)
BEGIN
SELECT u.user_id, u.Username, u.First_Name, u.Last_Name, r.Reservation_ID, r.Reservation_Date
FROM User u
INNER JOIN Book_Reservation r
ON u.user_id = r.user_id
INNER JOIN School s 
ON s.Name = u.School_Name
INNER JOIN operator o
ON o.Operator_ID = s.Operator_id
WHERE o.Username = operator
AND u.username LIKE CONCAT('%', username1, '%');
END//
DELIMITER ;

