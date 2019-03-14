# Analysis of SAP Careers Database

SAP's careers website at [https://jobs.sap.com](https://jobs.sap.com) contains thousand of jobs evolving around IT. Yet, the website's search functionality is fairly limited. This project was born out of the desire to quickly analyze and compare different job offerings specifically containing a particular phrase in the job title.

The [Jupyter notebook](https://github.com/mstykow/SAP_jobs/blob/master/SAP%20Careers%20Database.ipynb) aims to determine the most important requirements for a particular job and then build a model to predict a job title given a list of job requirements.

The data is extracted from [https://jobs.sap.com](https://jobs.sap.com) via a specifically built [web scraper](https://github.com/mstykow/SAP_jobs/blob/master/get_jobs.py). We also took this opportunity to experiment with other ways of fetching and storing data. To this end, we implemented [a simple Flask webservice](https://github.com/mstykow/SAP_jobs/blob/master/webservice.py) to run API queries against. Lastly, there is the option to [save scraped data in an SQL database](https://github.com/mstykow/SAP_jobs/blob/master/jobs_to_db.py).
