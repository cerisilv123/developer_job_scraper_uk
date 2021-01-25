import requests
import time
import csv
from bs4 import BeautifulSoup

#Function to scrape jobs from Monster Jobs 
def scrape_jobs_monster(location_input, role_type_input):
    location = location_input
    role_type = role_type_input

    URL = f'https://www.monster.co.uk/jobs/search?q={role_type.lower()}+developer+&where={location.lower()}&page=10'

    page = requests.get(URL)

    #Storing page HTML into soup object
    soup = BeautifulSoup(page.content, 'html.parser')

    #Storing the results section of the page (HTML) in to results and breaking up job elements
    results = soup.find(id='ResultsContainer')

    #Looping through and storing all job posting details in a JobPosting object
    job_posting_objs = []

    if results is not None: 
        job_elems = results.find_all('section', class_='card-content')
        
        for job_elem in job_elems:
            title_elem = job_elem.find('h2', class_='title')
            company_elem = job_elem.find('div', class_='company')
            location_elem = job_elem.find('div', class_='location')
            link_elem = job_elem.find('a')
                
            if None in (title_elem, company_elem, location_elem, link_elem):
                continue
            
            if role_type in title_elem.text.strip() or role_type.lower() in title_elem.text.strip():
                job = {"title": title_elem.text.strip(), "company": company_elem.text.strip(), "location": location_elem.text.strip(), "link": link_elem["href"]}
                job_posting_objs.append(job)
    
    return job_posting_objs

# Function to scrape jobs from Reed
def scrape_jobs_reed(location_input, role_type_input):
    website_title = "reed.co.uk"
    location = location_input
    role_type = role_type_input

    #List to store all JobPosting Objects
    job_posting_objs = []

    for x in range(2, 10):

        time.sleep(0.2) # slow down the number of requests made to server 

        URL = f"https://www.reed.co.uk/jobs/{role_type.lower()}-developer-jobs-in-{location.lower()}?pageno={x}"
        
        page = requests.get(URL)
        
        #Storing page HTML into soup object
        soup = BeautifulSoup(page.content, "html.parser")
        
        #Storing the results section of the page (HTML) in to results and breaking up job elements
        results = soup.find("div", id="content")

        website_title = "https://www.reed.co.uk"

        if results is not None:
            job_elems = results.find_all("article", class_="job-result")

            for job_elem in job_elems: 
                title_elem = job_elem.find("h3", class_="title")
                title_elem = title_elem.text.strip()
                company_elem = job_elem.find("a", class_="gtmJobListingPostedBy")
                company_elem = company_elem.text.strip()
                location_elem = job_elem.find("li", class_="location")
                location_elem = location_elem.find("span")
                location_elem = location_elem.text.strip()
                link_elem = job_elem.find("h3", class_="title")
                link_elem = link_elem.find("a")["href"]
                full_link = website_title + link_elem
                
                if None in (title_elem, company_elem, location_elem, link_elem):
                    continue

                job = {"title": title_elem, "company": company_elem, "location": location_elem, "link": full_link}
                job_posting_objs.append(job)
    
    #Printing out job postings
    return job_posting_objs

#Function to scrape jobs from jobsite.co.uk
def scrape_jobs_jobsite(location_input, role_type_input):
    location = location_input
    role_type = role_type_input

    job_posting_objs = []
    
    URL = f"https://www.jobsite.co.uk/jobs/{role_type.lower()}-developer/in-{location.lower()}?radius=20&page=2"
        
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find("div", class_="row job-results-row")

    if results is not None:
        job_elems = results.find_all("div", class_="job")
        
        for job_elem in job_elems:
            title_elem = job_elem.find("h2").text.strip()
            location_elem = location
            company_elem = job_elem.find("li", class_="company").text.strip()
            link_elem = job_elem.find("a")["href"]
            
            if None in (title_elem, location_elem, company_elem, link_elem):
                continue

            job = {"title": title_elem, "company": company_elem, "location": location_elem, "link": link_elem}
            job_posting_objs.append(job)

    return job_posting_objs            

# Function to scrape jobs from cvlibrary
def scrape_jobs_cvlibrary(location_input, role_type_input):
    website_title = "cvlibrary"
    location = location_input
    role_type = role_type_input

    job_posting_objs = []

    for x in range(1, 6):

        time.sleep(0.2) # slow down the number of requests made to server 

        URL = f"https://www.cv-library.co.uk/{role_type.lower()}-developer-jobs-in-{location.lower()}?distance=20&page={x}&us=1"

        page = requests.get(URL)
        
        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find("ol", id="searchResults")

        website_title = "https://www.cvlibrary.co.uk"

        if results is not None: 

            job_elems = results.find_all("li", class_="results__item")

            for job_elem in job_elems:
                title_elem = job_elem.find("a").text.strip()
                location_elem = location
                links = job_elem.find_all("a")
                company_elem = links[1].text.strip()
                link_elem = links[0]["href"]
                full_link = website_title + link_elem

                if None in (title_elem, location_elem, company_elem, link_elem):
                    continue

                if role_type in title_elem or role_type.lower() in title_elem:
                    job = {"title": title_elem, "company": company_elem, "location": location_elem, "link": full_link}
                    job_posting_objs.append(job)
    
    return job_posting_objs

# Function to write job results to CSV so user can download
def write_jobs_to_csv(job_results):
    with open("jobresults-download.csv", "w", newline="") as file: 
        file_writer = csv.writer(file)
        file_writer.writerow(["title", "company", "location", "link"])
        for dict_result in job_results:
            line_to_write = []
            for key in dict_result: 
                line_to_write.append(dict_result[key])
            file_writer.writerow(line_to_write)

        





