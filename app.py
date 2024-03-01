from flask import Flask, render_template, request, redirect, session
from flask_session import Session
from cs50 import SQL
from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required

app = Flask(__name__)
db = SQL("sqlite:///mook.db")

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
@login_required
def index():
	try:
		quote = db.execute("SELECT quote, title FROM quotes JOIN mooks ON quotes.mook_id = mooks.id WHERE user=?  ORDER BY random() LIMIT 1", session["user_id"])
		db.execute("SELECT quote, title FROM quotes JOIN mooks ON quotes.mook_id = mooks.id WHERE user=? ORDER BY random()", session["user_id"])[0]
	except IndexError:
		quote = '"Add quotes"'

	return render_template("index.html", quote=quote)

@app.route("/mymook", methods=["POST", "GET"])
@login_required
def mymook():
	if request.method == "POST":
		search = request.form.get("search").strip()
		if not search:
			return apology("Enter a valid search")
		if search[0] == " ":
			return apology("Enter a valid search")
	
		mooks = db.execute("SELECT * FROM mooks WHERE (title LIKE ('%' || ? || '%') OR author LIKE ('%' || ? || '%')) AND user=? ORDER BY id DESC", search, search, session["user_id"])
		return render_template("my-mook.html", mooks=mooks)

	if request.method == "GET":
		mooks = db.execute("SELECT * FROM mooks WHERE user=? ORDER BY id DESC", session["user_id"])
		return render_template("my-mook.html", mooks=mooks)
                         
            
@app.route("/add_book", methods=["POST", "GET"])
@login_required
def add_book():  
	if request.method == "POST":
		title = request.form.get("title")
		author = request.form.get("author")
		description = request.form.get("description")
		rating = float(request.form.get("rating"))
		urlimage = request.form.get("urlimage")
		length = request.form.get("length")
		if int(length) > 300:
			return apology("The description length must not exceed 300 characters")

		db.execute("INSERT INTO mooks (user, type, title, author, description, rating, img) VALUES(?, 'book', ?, ?, ?, ?, ?)", session["user_id"], title, author, description, rating, urlimage)      
		return redirect("/mymook")  
	if request.method == "GET":
		return render_template("add-book.html")
    
    
    
@app.route("/add_movie", methods=["POST", "GET"])
@login_required
def add_movie():

	if request.method == "POST":
		title = request.form.get("title")
		director = request.form.get("director")
		description = request.form.get("description")
		rating = float(request.form.get("rating"))
		urlimage = request.form.get("urlimage")
		length = request.form.get("length")
		if int(length) > 300:
			return apology("The description length must not exceed 300 characters")
  
		db.execute("INSERT INTO mooks (user, type, title, author, description, rating, img) VALUES(?, 'movie', ?, ?, ?, ?, ?)", session["user_id"], title, director, description, rating, urlimage)

		return redirect("/mymook")

	if request.method == "GET":
		return render_template("add-movie.html")

@app.route("/mytop")
@login_required
def mytop():
	if request.method == "POST":
		...

	if request.method == "GET":
		top = db.execute("SELECT * FROM mooks WHERE user=? ORDER BY rating DESC LIMIT 10", session["user_id"])
		return render_template("my-top.html", top=top)

@app.route("/add_quote", methods=["POST", "GET"])
@login_required
def addquote():
	if request.method == "GET":
		title = request.args.get("title")
		img = request.args.get("img")
		type = request.args.get("type")
		return render_template("add-quote.html", title=title, img=img, type=type)

	if request.method == "POST":
		q = '"'
		quote = q + request.form.get("quote") + q
		t = request.form.get("title")
		length = request.form.get("length")
		if int(length) > 300:
			return apology("The quote length must not exceed 300 characters")
		db.execute("INSERT INTO quotes (quote, mook_id) VALUES (?, (SELECT id FROM mooks WHERE title = ?))", quote, t)
		return redirect("/mymook")
        
    
    

@app.route("/myquotes", methods=["POST", "GET"])
@login_required
def myquotes():
	if request.method == "POST":
		search = request.form.get("search")
		
		quotes = db.execute("SELECT * FROM mooks JOIN quotes ON quotes.mook_id = mooks.id WHERE (title LIKE ('%' || ? || '%') OR author LIKE ('%' || ? || '%') OR quote LIKE (('%' || ? || '%'))) AND user=? ORDER BY quotes.id DESC", search, search, search, session["user_id"])
		return render_template("my-quotes.html", quotes=quotes)

	if request.method == "GET":
		quotes = db.execute("SELECT quote, img, title, author, type, quotes.id FROM quotes JOIN mooks ON quotes.mook_id = mooks.id WHERE user=? ORDER BY quotes.id DESC", session["user_id"])
		return render_template("my-quotes.html", quotes=quotes)

@app.route("/deletemook", methods=["POST"])
@login_required
def deletemook():
    id = request.form.get("qid")
    db.execute("DELETE FROM mooks WHERE id = ?", id)
    return redirect("/mymook")


@app.route("/deletequote", methods=["POST"])
@login_required
def deletequote():
    id = request.form.get("id")
    db.execute("DELETE FROM quotes WHERE id = ?", id)
    return redirect("/myquotes")
  
  
@app.route("/register", methods=["POST", "GET"])
def register():
	if request.method == "POST":
		user = request.form.get("user")

		if not user:
			return apology("You have to specify a username")

		existint_usernames = db.execute("SELECT username FROM users")
		for u in existint_usernames:
			if user == u["username"]:
				return apology("The username already exists")

		password = request.form.get("password")
		confirm = request.form.get("confirm")
  
		if not password:
			return apology("You have to specify a password")
		if not confirm:
			return apology("You have to enter a password confirmation")
		if password != confirm:
			return apology("Password and confirmation must coincide")

		db.execute("INSERT INTO users (username, password) VALUES (?, ?)", user, generate_password_hash(password))
  
		return redirect("/login")

	if request.method == "GET":
		return render_template("register.html")

@app.route("/login", methods=["POST", "GET"])
def login():
	session.clear()

	if request.method == "POST":
		user = request.form.get("user")
		if not user:
			return apology("You must enter a username")
		password = request.form.get("password")
		if not password:
			return apology("You must enter a password")

		rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("user"))

		if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
			return apology("invalid username and/or password")

		session["user_id"] = rows[0]["id"]

		return redirect("/")

	if request.method == "GET":
		return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    
    return redirect("/")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)