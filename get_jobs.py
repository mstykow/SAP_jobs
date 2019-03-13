#! python3
# Program web-scrapes https://jobs.sap.com for given a search string.

import os, sys, requests, webbrowser, bs4, csv, re

# Function to return number of hits given a search string
def get_hits(string):
    string = string.strip().lower()
    url_string = string.replace(' ', '+')
    url = 'https://jobs.sap.com/search/?q={}'.format(url_string)
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features="lxml")
    return int(soup.select('.paginationLabel > b')[1].text)

# Function to extract relevant links from the up to 25 results returned per page 
def search_page(string, page_after):
    string = string.strip().lower()
    url_string = string.replace(' ', '+')
    url = 'https://jobs.sap.com/search/?q={}'.format(url_string) \
        + '&startrow={}'.format(page_after)
    res = requests.get(url)
    res.raise_for_status()
    soup = bs4.BeautifulSoup(res.text, features="lxml")
    # CSS selector for link to job
    all_jobs = soup.select('.jobTitle.hidden-phone > .jobTitle-link')
    # Take only those jobs which have the search string in the title
    filtered_jobs = [job for job in all_jobs if string in job.text.lower()]
    # By choosing a dictionary, we omit jobs with the same job title as they are
    # often duplicates
    job_links = {job.text: 'https://jobs.sap.com' + job.get('href') \
        for job in filtered_jobs}
    return job_links

# Function to collect results from all result pages
def get_joblinks(string):
    job_links = {}
    for i in range(0, get_hits(string), 25):
        job_links.update(search_page(string, i))
    return job_links

# Function to extract all relevant features and return them as a list of lists given
# a dict of job titles with job links
def job_results(job_links):
    # List of features to extract
    feature_classes = {'Date Posted': 'datePosted', 'Location': 'jobLocation'}
    job_desc = ['Requisition ID', 'Expected Travel', 'Career Status', 'Employment Type']
    req = ['skill', 'competencies', 'requirement', 'bonus', 'pre-requisite', \
        'prerequisite', 'experience', 'you have achieved', \
        'competency', 'who you are', 'education', 'qualification', 'what do you need', \
        'qualifications', 'requirements', 'prerequisites', 'experiences', 'skills', \
        'you will need', 'also have']
    jobs = [['Job Title'] + list(feature_classes.keys()) + job_desc + \
        ['Requirements']]
    for title, link in job_links.items():
        job_data = [title]
        res = requests.get(link)
        res.raise_for_status()
        soup = bs4.BeautifulSoup(res.text, features = "lxml")
        
        # Extract 'feature_classes'
        for feature in feature_classes.values():
            feature_tag = soup.select('span[itemprop = "{}"]'.format(feature))[0]
            # Strip spaces, tabs, and newlines
            feature_value = feature_tag.text.strip('\t\n\r ')
            job_data.append(feature_value)
        
        # Extract 'job_desc' from the job description block
        job_desc_tags = soup.select('.jobdescription > p > span > span > strong')
        job_desc_dict_all = {tag.text.strip(': '): tag.next_sibling \
            for tag in job_desc_tags}
        job_desc_list_wanted = [job_desc_dict_all.get(key) for key in job_desc]
        job_data.extend(job_desc_list_wanted)

        # Extract 'req' from job description block
        req_tags = soup.select('.jobdescription > p')
        job_req = ''
        flag = None
        for tag in req_tags:
            # Check if tag is a sub-header and contains any of the req key words
            hit1 = any(key in tag.text.lower() for key in req \
                if len(tag.text.split()) <= 8)
            # Check if tag begins (first three words) with any of the req key words
            hit2 = any(key in tag.text.lower().split()[0:2] for key in req)
            if hit1:
                # Find 1st and 2nd sib to current tag that are not NavigableStrings
                first_sib = tag.next_sibling
                while isinstance(first_sib, bs4.element.NavigableString) or \
                    first_sib.text == '\xa0':
                    first_sib = first_sib.next_sibling
                second_sib = first_sib.next_sibling
                while isinstance(second_sib, bs4.element.NavigableString) or \
                    second_sib.text == '\xa0':
                    second_sib = second_sib.next_sibling
                # Fetch first sibling
                if first_sib:
                    job_req = re.sub(r'\n+', '\n', job_req + \
                        first_sib.text).strip('\t\n\r ') + '\n'
                # Fetch second sibling if longer than 8 words (not a sub-heading)
                if second_sib and len(second_sib.text.split()) > 8 and \
                    first_sib.name != 'ul':
                    job_req = re.sub(r'\n+', '\n', job_req + \
                        second_sib.text).strip('\t\n\r ') + '\n'
            elif hit2:
                    job_req = re.sub(r'\n+', '\n', job_req + \
                        tag.text).strip('\t\n\r ') + '\n'
        job_data.append(re.sub(r'\xa0', ' ', job_req).strip('\t\n\r '))

        # Append finished job to list
        jobs.append(job_data)
    return jobs

# Wrapper function to get all jobs matching a search string as a list of lists
def get_jobs(string):
    print('Fetching results...') # display text while downloading
    jobs = job_results(get_joblinks(string))
    print('Done.')
    print('Found {} results.'.format(len(jobs) - 1))
    return jobs

# Wrapper function to get all jobs matching a search string as a csv file
def get_jobs_csv(string):
    print('Writing results to file "{}.csv"...'.format(string))
    # Get the path to the current working directory
    base_path = os.path.dirname(sys.argv[0])
    os.chdir(base_path)
    csv_data = job_results(get_joblinks(string))
    # Write data to csv
    with open('{}.csv'.format(string), 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerows(csv_data)
    print('Done.')
    print('Found {} results.'.format(len(csv_data) - 1))