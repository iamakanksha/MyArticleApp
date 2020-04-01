# MyArticleApp
A web app created using flask, which allows registered users to publish their thoughts through articles

To run the codes:
python app.py

DB TABLES (in MYSQL)
CREATE TABLE users (id INT(10) AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), emailid VARCHAR(100), username VARCHAR(30) NOT NULL, password VARCHAR(100) NOT NULL, register_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP);

CREATE TABLE articles (id INT(10) AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), author VARCHAR(255), body TEXT, date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP) 
