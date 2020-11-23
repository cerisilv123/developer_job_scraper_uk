from flask import Flask, redirect, url_for, render_template, request, session, flash
from datetime import timedelta
import job_scraper
import concurrent.futures

app = Flask(__name__)

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
        search_results = request.form["language_selected"]
        search_location = request.form["location_selected"]
        return redirect(url_for("results", results = search_results, location = search_location))
    else: 
        job_results = []
        # Scraping jobs - Using multithreading to run functions in parallel and speed up scraping speed
        with concurrent.futures.ProcessPoolExecutor() as executor: 
            job_results_monster = executor.submit(job_scraper.scrape_jobs_monster, location, results)
            job_results_reed = executor.submit(job_scraper.scrape_jobs_reed, location, results)
            job_results_jobsite = executor.submit(job_scraper.scrape_jobs_jobsite, location, results)
            job_results_cvlibrary = executor.submit(job_scraper.scrape_jobs_cvlibrary, location, results)
            job_results += job_results_monster.result()
            job_results += job_results_reed.result()
            job_results += job_results_jobsite.result()
            job_results += job_results_cvlibrary.result()

        return(render_template("results.html", job_results = job_results))
    
if __name__ == "__main__":
    app.run(debug=True)