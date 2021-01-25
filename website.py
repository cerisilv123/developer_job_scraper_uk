from flask import Flask, redirect, url_for, render_template, request, session, flash, send_file
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
import job_scraper
import concurrent.futures
import secrets

app = Flask(__name__)

random_session_key = secrets.token_urlsafe(16) # Create a random key varable to encrypt session on server
app.secret_key = random_session_key

app.config['SQLAlchemy_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALchemy_TRACK_MODIFICATION'] = False # Wont show errror message when making change to db
db = SQLAlchemy(app)

# DB MODELS
class User(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    user_email = db.Column(db.String(100))
    user_password = db.Column(db.String(100))

    def __init__(self, email, password):
        self.user_email = email
        self.user_password = password

# ROUTES
@app.route("/", methods = ["POST", "GET"])
def home():
    if request.method == "POST":
        search_results = request.form["language_selected"]
        search_location = request.form["location_selected"]
        return(redirect(url_for("results", results = search_results, location=search_location)))
    else: 
        return render_template("index.html")

@app.route("/results/<results>/<location>", methods = ["POST", "GET"])
def results(results, location):
    if request.method == "POST":
        if request.form["button"] == "submit": # User wants to scrape jobs 
            search_results = request.form["language_selected"]
            search_location = request.form["location_selected"]
            return redirect(url_for("results", results = search_results, location = search_location))
        elif request.form["button"] != "submit": # User wants to download jobs to CSV file
            return redirect(url_for("download"))
    else: 
        job_results = []
        # Scraping jobs - Using multithreading to run functions in parallel and speed up scraping speed
        with concurrent.futures.ProcessPoolExecutor() as executor: 
            job_results_monster = executor.submit(job_scraper.scrape_jobs_monster, location, results)
            job_results_reed = executor.submit(job_scraper.scrape_jobs_reed, location, results)
            # job_results_jobsite = executor.submit(job_scraper.scrape_jobs_jobsite, location, results)
            job_results_cvlibrary = executor.submit(job_scraper.scrape_jobs_cvlibrary, location, results)
            job_results += job_results_monster.result()
            job_results += job_results_reed.result()
            # job_results += job_results_jobsite.result()
            job_results += job_results_cvlibrary.result()

        job_scraper.write_jobs_to_csv(job_results)

        return(render_template("results.html", job_results = job_results))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["form_email_login"]
        password = request.form["form_password_login"]
        found_user_email = User.query.filter_by(user_email = email).first() 
        found_user_password = User.query.filter_by(user_password = password).first()
        if found_user_email != None and found_user_password != None: 
            found_user_email = found_user_email.user_email
            found_user_password = found_user_password.user_password
            if found_user_email == email and found_user_password == password:
                session["user_session"] = email # Creating a session and storing the users email in session object
                return(redirect(url_for("home")))
            else: 
                flash("Details are incorrect, please try again!")
                return(redirect(url_for("login")))
        else: 
            flash("Woops! Details are incorrect, please try again!")
            return(redirect(url_for("login")))
    else: 
        if "user_session" in session: 
            flash("You are already logged in!")
            return redirect(url_for("home"))
        else: 
            return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_session" in session: # This would only occur if user heads to link indirectly
        flash("You need to log out first before you can register another account.")
        return redirect(url_for("home"))
    if request.method == "POST":
        email = request.form["form_email_register"]
        password = request.form["form_password_register"]
        user_account = User(email, password)
        found_user_email = User.query.filter_by(user_email = email).first() # Checking to see if email already exists in DB
        if found_user_email != None: 
            found_user_email = found_user_email.user_email
        if found_user_email == email: 
            flash("Sorry, this email already exists!")
            return redirect(url_for("register"))
        else: 
            db.session.add(user_account)
            db.session.commit()
            return redirect(url_for("login"))
    else: 
        return render_template("register.html")

@app.route("/logout")
def logout():
    if "user_session" in session:
        session.pop("user_session", None) # Logging user out of session
        flash("You have been logged out!")
    return redirect(url_for("login"))

@app.route("/download")
def download():
    try:
        return send_file("jobresults-download.csv", attachment_filename="jobresults-download.csv")
    except: 
        abort(404)
    flash("Downloading search results.. :)")
    return redirect(url_for("home"))
   
if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)