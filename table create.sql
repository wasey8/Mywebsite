CREATE TABLE data
(
id SERIAL PRIMARY KEY,
fullname VARCHAR NOT NULL,
email VARCHAR NOT NULL,
password VARCHAR NOT NULL
);

CREATE TABLE books
(
id SERIAL PRIMARY  KEY,
isbn VARCHAR NOT NULL,
title VARCHAR NOT NULL,
author VARCHAR NOT NULL,
year integer NOT NULL
);



create table reviews
  (id SERIAL PRIMARY KEY,
     review VARCHAR NOT NULL,
     book_isbn integer REFERENCES books,
      rating INTEGER,
       author VARCHAR REFERENCES data
     );

     INSERT INTO books (isbn,title,author,year) Values ('978-969-0-02341-4','Pir-e-Kamil','Umera Ahmad','2004');
     INSERT INTO books (isbn,title,author,year) Values ('11111116','Shehr-e-Zaat','Umera Ahmad','2002');
     INSERT INTO books ("isbn","title","author","year") Values ("978-969-0-02341-4","Pir-e-Kamil","Umera Ahmad","2004")
     INSERT INTO books ("isbn","title","author","year") Values ("978-969-0-02341-4","Pir-e-Kamil","Umera Ahmad","2004")
     INSERT INTO books ("isbn","title","author","year") Values ("978-969-0-02341-4","Pir-e-Kamil","Umera Ahmad","2004")
