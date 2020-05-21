import os,requests, json
from flask import Flask, session,request,render_template,flash,url_for,redirect,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from passlib.hash import pbkdf2_sha256
from passlib.hash import sha256_crypt

# from helpers import get_review_counts, login_required, get_averadge_rating

# Libraries import

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
engine = create_engine(("postgres://dcziezsoloamhj:d290f09c1c05929523fc10488be4c646307cb0209494f8359de29b950e72b09f@ec2-18-214-211-47.compute-1.amazonaws.com:5432/d7t82op26rloqn"))
db = scoped_session(sessionmaker(bind=engine))

# Setting up database


@app.route("/")
def home():
    return render_template("home.html")

# Homepage

@app.route("/hello",  methods=["POST","GET"])
def hello():
    if request.method=="POST":
        fullname = request.form.get("fullname")
        password = request.form.get("password")
        session['fullname']=fullname
        data=db.execute("SELECT fullname FROM data WHERE fullname=:fullname",{"fullname":fullname}).fetchone()
        data2=db.execute("SELECT password FROM data WHERE fullname=:fullname",{"fullname":fullname}).fetchone()

        if data is None:
            flash("Incorrect username")
            return redirect(url_for('home'))
        else:
            for i in data2:
                if sha256_crypt.verify(password,i):
                    flash("Login successfull!")
                    return render_template("hello.html",fullname=fullname)
                flash("Invalid password")
                return redirect(url_for('home'))
    return render_template("home.html")



#For Homepage login



@app.route("/signup", methods=["GET","POST"])
def sign():
    if request.method=="POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        usernamedata=db.execute("SELECT fullname FROM data WHERE fullname=:fullname",{"fullname":fullname}).fetchone()
        usernamedata1=db.execute("SELECT email FROM data WHERE email=:email",{"email":email}).fetchone()
        usernamedata2=db.execute("SELECT password FROM data WHERE password=:password",{"password":password}).fetchone()
        hash=sha256_crypt.hash(password)

        if usernamedata is None and usernamedata1 is None and usernamedata2 is None :
            db.execute("INSERT INTO data(fullname,email,password) VALUES(:fullname,:email,:password)",
            {"fullname":fullname,"email":email,"password":hash})
            db.commit()
            flash("Account created successfully!")
            return redirect(url_for('home'))
        else:
            flash("Try different credentials")
            return redirect(url_for('sign'))
    return render_template("signup.html")


# For signup


@app.route("/logout")
def logout():
     if 'fullname' in session:
         session.pop('fullname',None)
         flash("logout successfull!")
         return redirect(url_for('home'))

# For logout


@app.route("/search",  methods=["POST","GET"])
def search():
    if request.method=="POST":
         isbn=request.form.get("isbn").lower().strip()
         title=request.form.get("title").lower().strip()
         author=request.form.get("author").lower().strip()
         books=db.execute("SELECT * FROM books where LOWER(isbn) like :isbn and LOWER(title) like :title and LOWER(author) like :author", {"isbn": f"%{isbn}%","title": f"%{title}%","author":f"%{author}%" }).fetchall()
         return render_template("books.html",books=books, isbn=isbn,author=author,title=title)
    return render_template("hello.html")



# For book information
@app.route("/review/<isbn>", methods=["GET", "POST"])
def review(isbn):

    currentUser = session["fullname"]
    row = db.execute("SELECT isbn FROM books WHERE isbn= :isbn",{"isbn":isbn})
    bookId = row.fetchone()
    bookId = bookId[0]

    #Fetching user ID.
    row2 = db.execute("SELECT id FROM data where fullname= :fullname", {"fullname":currentUser})
    userId = row2.fetchone()
    userId = userId[0]
    session["reviews"]=[]
    if request.method == "POST":
        user_review = db.execute("SELECT * FROM reviews WHERE author = :fullname AND book_isbn = :isbn",
                            {"fullname": session["fullname"], "isbn": isbn} )
        userreview = user_review.first()
        if not userreview:
            review = request.form.get("review")
            rating = request.form.get("rating")
            db.execute("INSERT INTO reviews (review, book_isbn, rating, author) VALUES (:review, :isbn, :rating, :author)",
                        {"review": review, 'isbn': isbn, "rating": rating, "author": session["fullname"]})
            db.commit()
        else:
            return render_template("error.html", error="you already submitted review for this book")
        return redirect(url_for("review", isbn=isbn))
    else:
        book = db.execute("SELECT isbn, title, author, year FROM books WHERE isbn = :isbn",{"isbn": isbn}).fetchone()
        reviews = db.execute("SELECT * FROM reviews WHERE book_isbn = :isbn",{"isbn": isbn}).fetchall()
        res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"key": "Zw4O0lhRwdENOdrZKB87A", "isbns": isbn})
        data = res.json()
        avgrating = data["books"][0]["average_rating"]
        rating_work = data["books"][0]["work_ratings_count"]


    return render_template("review.html", book=book, avgrating=avgrating, rating_work=rating_work, reviews=reviews)





# for api
@app.route("/api/<isbn>")
def api(isbn):
    book_detail=db.execute("SELECT author,title,year,isbn FROM books Where isbn=:isbn",{"isbn":isbn}).fetchone()
    review_stats=db.execute("SELECT avg(rating),count(review) FROM books JOIN reviews r on book_isbn=r.book_isbn WHERE isbn=:isbn GROUP BY book_isbn ",{"isbn":isbn}).fetchone()
    if review_stats==None:
        review_count=0
        average_score=None
    else:
        review_count=review_stats[1]
        average_score=review_stats[0]

    if book_detail!=None:
        res={
        "title":book_detail[0],
        "author":book_detail[1],
        "year":book_detail[2],
        "isbn":book_detail[3],
        "review_count":review_count,
        "average_count":average_score
        }
        return jsonify(res)
    return abort(404)
