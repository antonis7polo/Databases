
--3.1.1
SELECT School.Name, COUNT(*) as Total_Rentals
FROM Rental
INNER JOIN User ON Rental.User_ID = User.User_ID
INNER JOIN School ON User.School_Name = School.Name
WHERE Rental.Rental_Date BETWEEN [start_date] AND [end_date]
GROUP BY School.Name;


--3.1.2 
SELECT DISTINCT Author.Author_ID, Author.First_Name, Author.Last_Name
FROM Author
INNER JOIN Book_Author ON Author.Author_ID = Book_Author.Author_ID
INNER JOIN Book_Category ON Book_Author.ISBN = Book_Category.ISBN
INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id
WHERE Category.Genre = [genre];


SELECT DISTINCT User.User_ID, User.Username, User.First_Name, User.Last_Name, User.School_Name
FROM User
INNER JOIN Rental ON User.User_ID = Rental.User_ID
INNER JOIN Book_Category ON Rental.ISBN = Book_Category.ISBN
INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id
WHERE Category.Genre = [genre]
AND User.Is_Teacher = TRUE
AND Rental.Rental_Date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);



--3.1.3
SELECT User.User_ID, User.First_Name, User.Last_Name, User.School_Name, COUNT(*) AS Number_Of_Rentals
FROM User
INNER JOIN Rental ON User.User_ID = Rental.User_ID
WHERE User.Is_Teacher = TRUE
  AND User.Date_Of_Birth > DATE_SUB(CURDATE(), INTERVAL 40 YEAR)
GROUP BY User_ID
ORDER BY Number_Of_Rentals DESC
LIMIT 20;

--3.1.4
SELECT Author.Author_ID, Author.First_Name, Author.Last_Name
FROM Author
INNER JOIN Book_Author ON Author.Author_ID = Book_Author.Author_ID
LEFT JOIN Rental ON Book_Author.ISBN = Rental.ISBN
GROUP BY Author.Author_ID
HAVING COUNT(Rental.Rental_ID) = 0;


--3.1.5
SELECT o.Operator_ID, o.username, o.First_Name, o.Last_Name, COUNT(*) AS Num_Rentals
FROM Operator o
INNER JOIN School s ON o.Operator_ID = s.Operator_id
INNER JOIN User u ON s.Name = u.School_Name
INNER JOIN Rental r ON r.User_ID = u.User_ID
WHERE r.Rental_Date BETWEEN [start_date] AND [end_date]
GROUP BY o.Operator_ID
HAVING Num_Rentals > 20
  AND COUNT(*) = SOME(
    SELECT COUNT(*)
    FROM Operator o1
    INNER JOIN School s1 ON o1.Operator_ID = s1.Operator_id
    INNER JOIN User u1 ON s1.Name = u1.School_Name
    INNER JOIN Rental r1 ON r1.User_ID = u1.User_ID
    WHERE r1.Rental_Date BETWEEN [start_date] AND [end_date]
      AND o.Operator_ID <> o1.Operator_ID
    GROUP BY o1.Operator_ID
  )
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
SELECT DISTINCT b.Title, a.First_Name, a.Last_Name
FROM Operator o
INNER JOIN School s ON s.operator_id = o.operator_id
INNER JOIN School_Books sb ON sb.School_Name = s.Name
INNER JOIN Book b ON sb.ISBN = b.ISBN
INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
INNER JOIN Author a ON a.Author_ID = ba.Author_ID
INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN
INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID
WHERE o.username = [username]
  AND b.Title LIKE CONCAT('%', [title], '%')
  AND c.Genre LIKE CONCAT('%', [genre], '%')
  AND a.First_Name LIKE CONCAT('%', [first_name], '%')
  AND a.Last_Name LIKE CONCAT('%', [last_name], '%')
  AND (sb.Available_Copies >= [min_copies]);




--3.2.2
SELECT DISTINCT u.User_ID, u.Username, u.First_Name, u.Last_Name
FROM User u
INNER JOIN Rental r ON u.user_id = r.user_id
INNER JOIN School s ON s.Name = u.School_Name
INNER JOIN Operator o ON o.Operator_ID = s.Operator_ID
WHERE r.Return_Date IS NULL
  AND DATEDIFF(CURDATE(), r.Rental_Date) > 7
  AND u.First_Name LIKE CONCAT('%', [first_name], '%')
  AND u.Last_Name LIKE CONCAT('%', [last_name], '%')
  AND DATEDIFF(CURDATE(), r.Rental_Date + 7) >= [days]
  AND o.Username = [operator_username];



--3.2.3
--a
SELECT User.User_ID, User.Username, Category.Genre, AVG(Published_Book_Review.Likert_Review) AS avg_reviews_per_user_and_category
FROM User 
INNER JOIN Published_Book_Review ON User.User_ID = Published_Book_Review.User_ID 
INNER JOIN Book_Category ON Published_Book_Review.ISBN = Book_Category.ISBN 
INNER JOIN Category ON Book_Category.Category_Id = Category.Category_Id 
INNER JOIN Rental ON User.User_ID = Rental.Rental_ID
WHERE Category.Genre LIKE CONCAT('%', [genre_value], '%')
AND User.Username LIKE CONCAT('%', [username_value], '%')
AND User.School_Name = [school_name_value]
GROUP BY User.User_ID, Category.Category_ID

--b
SELECT User.User_ID, User.Username, User.First_Name, User.Last_Name, AVG(Published_Book_Review.Likert_Review) 
FROM User
INNER JOIN Published_Book_Review ON User.User_ID = Published_Book_Review.User_ID
INNER JOIN Rental ON User.User_ID = Rental.Rental_ID
WHERE User.Username = [username_value]
GROUP BY User.User_ID

SELECT Category.Genre, AVG(Published_Book_Review.Likert_Review)
FROM Category 
INNER JOIN Book_Category ON Category.Category_ID = Book_Category.Category_ID
INNER JOIN Published_Book_Review ON Book_Category.ISBN = Published_Book_Review.ISBN
INNER JOIN User ON Published_Book_Review.User_ID = User.User_ID
INNER JOIN Rental ON User.User_ID = Rental.Rental_ID
WHERE Category.Genre = [genre_value]
AND User.School_Name = %s
GROUP BY Category.Category_ID


--3.3.1
SELECT DISTINCT b.ISBN, b.Title, a.First_Name, a.Last_Name
FROM User u
INNER JOIN School_Books sb ON sb.School_Name = u.School_Name
INNER JOIN Book b ON sb.ISBN = b.ISBN
INNER JOIN Book_Author ba ON ba.ISBN = b.ISBN
INNER JOIN Author a ON a.Author_ID = ba.Author_ID
INNER JOIN Book_Category bcat ON b.ISBN = bcat.ISBN
INNER JOIN Category c ON bcat.Category_ID = c.Category_ID
INNER JOIN Book_Keyword bk ON b.ISBN = bk.ISBN
INNER JOIN Keyword k ON bk.Keyword_ID = k.Keyword_ID
WHERE u.username = [username]
  AND b.Title LIKE CONCAT('%', [title], '%')
  AND c.Genre LIKE CONCAT('%', [genre], '%')
  AND a.First_Name LIKE CONCAT('%', [first_name], '%')
  AND a.Last_Name LIKE CONCAT('%', [last_name], '%');


INSERT INTO Book_Reservation (ISBN, User_ID, Reservation_Date)
VALUES ([ISBN_value], [User_ID_value], CURDATE());

--3.3.2
SELECT DISTINCT Book.ISBN, Book.Title, Rental.Rental_Date, Rental.Return_Date
FROM Rental
INNER JOIN Book ON Rental.ISBN = Book.ISBN
INNER JOIN User ON Rental.User_ID = User.User_ID
WHERE User.Username = [username];

