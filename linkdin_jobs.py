#Import dependencies
import requests
from bs4 import BeautifulSoup
import random
import pandas as pd
import spacy

known_tech_skills = [
    "Python", "Golang", "Go", "AWS", "Java", "JavaScript", "React", "Node.js",
    "SQL", "MongoDB", "PostgreSQL", "Docker", "Kubernetes", "Git", "HTML", "CSS",
    "C++", "C#", "Linux", "Flask", "Django", "TensorFlow", "PyTorch", "Hadoop",
    "Spark", "Machine Learning", "Deep Learning", "REST API", "CI/CD", "Agile",
    "MySQL", "MongoDB", "GCP", "Azure", "Jenkins", "Ansible", "Terraform", "DevOps",
    "Matplotlib", "Plotly", "Front-end", "Back-end", "QT", "QML", "GUI", 
    "Geographic Information System", "GIS", "FPGA", "OpenCV", "CUDA", "OpenCL", "Spacy",
    "NLTK", "Pandas", "NumPy", "Scikit-learn", "Keras", "FastAPI", "GraphQL", "NLP"
]


known_tech_qualifications = [
    'BTech', 'MTech', 'MCA', 'BCA', 'B.Sc', 'M.Sc', 'Bachelor', 'Master', 'Graduate',
    'Post Graduate', 'PHD', 'Computer Science', 'Engineering', 'Computer Application'
]

# Load English tokenizer, tagger, parser, NER, and word vectors
nlp = spacy.load("en_core_web_sm")


# Function to scrape job skills from a LinkedIn job page
def extract_skills(job_data, known_skills):
    found_skills = set()

    # Go through all the category texts
    for category, texts in job_data.items():
        for text in texts:
            doc = nlp(text)
            for token in doc:
                if token.text in known_skills:
                    found_skills.add(token.text)
            # Also check for multi-word skill phrases
            for phrase in known_skills:
                if phrase.lower() in text.lower():
                    found_skills.add(phrase)

    return list(sorted(found_skills))


# Function to scrape job qualifications from a LinkedIn job page
def extract_qualifications(job_data, known_qualifications):
    found_qualifications = set()

    # Go through all the category texts
    for category, texts in job_data.items():
        for text in texts:
            doc = nlp(text)
            for token in doc:
                if token.text in known_qualifications:
                    found_qualifications.add(token.text)
            # Also check for multi-word skill phrases
            for phrase in known_qualifications:
                if phrase.lower() in text.lower():
                    found_qualifications.add(phrase)

    return list(sorted(found_qualifications))


# Function to scrape job details from a LinkedIn job page
def extract_job_details(job_soup):

    soup = job_soup

    job_details = {}

    # Locate the main job description container
    description_section = soup.find("div", class_="show-more-less-html__markup")

    if description_section:
        current_category = "General Information"  # Default category
        job_details[current_category] = []

        # Extract all elements inside the description
        for element in description_section.children:
            if element.name in ["h3", "p", "strong"]:
                # Update category if we find a new heading, but preserve previous data
                current_category = element.get_text(strip=True)
                if current_category not in job_details:
                    job_details[current_category] = []
            elif element.name == "ul":
                # Extract list items under the current category
                items = [li.get_text(strip=True) for li in element.find_all("li")]
                job_details[current_category].extend(items)
            elif element.name and element.name not in ["br", "ul"]:
                # Extract any remaining text (e.g., paragraphs not inside lists)
                text = element.get_text(strip=True)
                if text:
                    job_details[current_category].append(text)

    else:
        job_details["General Information"] = "No description available"

    return job_details


def linkdin(title, location, user_skills, user_qualifications):
    # Construct the URL for LinkedIn job search
    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&f_TP=1"

    # Send a GET request to the URL and store the response
    response = requests.get(list_url)

    #Get the HTML, parse the response and find all list items(jobs postings)
    list_data = response.text
    list_soup = BeautifulSoup(list_data, "html.parser")
    page_jobs = list_soup.find_all("li")

    #Create an empty list to store the job postings
    id_list = []
    link_dict = {}

    #Itetrate through job postings to find job ids
    for i, job in enumerate(page_jobs):
        base_card_div = job.find("div", {"class": "base-card"})
        job_id = base_card_div.get("data-entity-urn").split(":")[3]

        link_tag = job.find("a", {"class": "base-card__full-link"})
        # Extract the href attribute
        if link_tag and link_tag.has_attr("href"):
            href_link = link_tag["href"]
        else:
            href_link = None  # Handle case where no href is found
        link_dict[job_id]= href_link
        '''print(job_id)'''
        id_list.append(job_id)

    # Initialize an empty list to store job information
    job_list = []

    # Loop through the list of job IDs and get each URL
    for key in link_dict:
        job_id = key
        # Construct the URL for each job using the job ID
        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"

        # Send a GET request to the job URL and parse the reponse
        job_response = requests.get(job_url)
        '''print(job_response.status_code)'''
        job_soup = BeautifulSoup(job_response.text, "html.parser")

        # Create a dictionary to store job details
        job_post = {}

        # Try to extract and store the job title
        try:
            job_post["Job Title"] = job_soup.find("h2", {"class":"top-card-layout__title font-sans text-lg papabear:text-xl font-bold leading-open text-color-text mb-0 topcard__title"}).text.strip()
        except:
            job_post["Job Title"] = None

        # Try to extract and store the company name
        try:
            job_post["Company Name"] = job_soup.find("a", {"class": "topcard__org-name-link topcard__flavor--black-link"}).text.strip()
        except:
            job_post["Company Name"] = None

        # Try to extract and store the company location
        try:
            job_post["Location"] = job_soup.find("span", {"class": "topcard__flavor topcard__flavor--bullet"}).text.strip()
        except:
            job_post["Location"] = None

        # Try to extract and store the time posted
        try:
            job_post["Time Posted"] = job_soup.find("span", {"class": "posted-time-ago__text topcard__flavor--metadata"}).text.strip()
        except:
            job_post["Time Posted"] = None

        # Try to extract and store the number of applicants
        try:
            job_post["No of Applicants"] = job_soup.find("span", {"class": "num-applicants__caption topcard__flavor--metadata topcard__flavor--bullet"}).text.strip()
        except:
            job_post["No of Applicants"] = None

        # Adding the Apply link
        try:
            job_post["Apply Link"] = link_dict[job_id]
        except:
            job_post["Apply Link"] = None

        # Extract job tech skills
        job_data = extract_job_details(job_soup)
        skills = extract_skills(job_data, known_tech_skills)

        # Extract job tech qualifications
        qualifications = extract_qualifications(job_data, known_tech_qualifications)
        '''print(qualifications)'''

        #Matching the skill with individual job skills
        Skill_Match=0
        for skill in user_skills:
            if skill in skills:
                Skill_Match += 1

        #Matching the qualification with individual job qualification
        Qualification_Match=0
        for qualification in user_qualifications:
            if qualification in qualifications or len(qualifications)==0:
                Qualification_Match = 1
                break

        #Add the match in dictionary
        job_post["Skill Match"] = Skill_Match
        job_post["Qualification Match"] = Qualification_Match

        # Add extracted skills and qualification to the dictionary
        job_post["Skills"] = skills
        job_post["Qualifications"] = qualifications

        # Adding the Apply link
        job_post["Apply Link"] = link_dict.get(job_id, "NONE")

        # Append the job details to the job_list
        job_list.append(job_post)
    
    # Create a pandas DataFrame using the list of job dictionaries 'job_list'
    jobs_df = pd.DataFrame(job_list)

    # Filter where Qualification match is 1
    filter_jobs = jobs_df[jobs_df['Qualification Match']==1]

    # Sort by 'Match' in descending order and display top 4
    top_matches = filter_jobs.sort_values(by='Skill Match', ascending=False).head(4)

    return top_matches


# Example usage
if __name__ == "__main__":
    # Example user input
    title = "Software Engineer"
    location = "India"
    user_skills = ["Python", "Java", "AWS"]
    user_qualifications = ["BTech", "MTech"]

    # Call the function and print the result
    result_df = linkdin(title, location, user_skills, user_qualifications)
    # Display the result
    print("Top 4 Job Matches:")
    print("-" * 60)
    # Display the DataFrame
    for index, row in result_df.iterrows():
        print(f"Job Title: {row['Job Title']}")
        print(f"Company Name: {row['Company Name']}")
        print(f"Location: {row['Location']}")
        print(f"Apply Link: {row['Apply Link']}")
        print(f"Skills: {', '.join(row['Skills'])}")
        print(f"Qualifications: {', '.join(row['Qualifications'])}")
        print(f"Skill Match: {row['Skill Match']}")
        print(f"Qualification Match: {row['Qualification Match']}")
        print(f"Time Posted: {row['Time Posted']}")
        print(f"No of Applicants: {row['No of Applicants']}")
        print("-" * 60)