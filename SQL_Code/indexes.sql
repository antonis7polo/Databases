CREATE INDEX idx_rental_date ON Rental(Rental_Date);
CREATE INDEX idx_title ON Book(Title);
CREATE INDEX idx_author ON Author(First_Name,Last_Name);
CREATE INDEX idx_available_copies ON School_Books(Available_Copies);
CREATE UNIQUE INDEX idx_genre ON Category(Genre);



