CREATE DATABASE Bookstore;
USE Bookstore;

CREATE TABLE Books (
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    PublishingYear YEAR,
    BookName VARCHAR(255),
    Author VARCHAR(255),
    LanguageCode VARCHAR(10),
    AuthorRating ENUM('Novice', 'Intermediate', 'Expert'),
    BookAverageRating FLOAT,
    BookRatingsCount INT,
    Genre VARCHAR(100),
    GrossSales FLOAT,
    PublisherRevenue FLOAT,
    SalePrice FLOAT,
    SalesRank INT,
    Publisher VARCHAR(255),
    UnitsSold INT
);

LOAD DATA INFILE '"C:\Users\vasus\OneDrive\Desktop\Books_Data_Clean.csv"'
INTO TABLE Books
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(PublishingYear, BookName, Author, LanguageCode, AuthorRating, BookAverageRating, BookRatingsCount, Genre, GrossSales, PublisherRevenue, SalePrice, SalesRank, Publisher, UnitsSold);

-- Retrieve operation example
SELECT * FROM Books WHERE Genre = 'fiction';

-- Insert operation example
INSERT INTO Books (PublishingYear, BookName, Author, LanguageCode, AuthorRating, BookAverageRating, BookRatingsCount, Genre, GrossSales, PublisherRevenue, SalePrice, SalesRank, Publisher, UnitsSold)
VALUES (2024, 'New Book Title', 'New Author', 'eng', 'Expert', 4.5, 100, 'non-fiction', 10000.00, 6000.00, 20.00, 1, 'New Publisher', 500);

-- Modify operation example
UPDATE Books
SET BookName = 'Updated Book Title', Author = 'Updated Author'
WHERE BookID = 1;