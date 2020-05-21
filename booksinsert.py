import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


engine = create_engine(("postgres://ztobzjfaefwyju:838d4eeef5fdc1502a0722a5a5a6a210bd032848fae8f7606767942b51356528@ec2-52-87-135-240.compute-1.amazonaws.com:5432/d2re0a9kttjkdr"))
db = scoped_session(sessionmaker(bind=engine))

def add():
    f=open("books.csv")
    reader=csv.reader(f)
    for isbn,title,author,year in reader:
        db.execute("INSERT INTO books(isbn,title,author,year) VALUES (:isbn,:title,:author,:year)",
        {"isbn":isbn,"title":title,"author":author,"year":year})
        print(f" {isbn} {title} {author} {year}")
    db.commit()
    print("Data inserted successfully")
add()
