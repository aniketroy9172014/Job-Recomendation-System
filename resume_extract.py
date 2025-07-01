import re
import pdfplumber
import spacy
import nltk

nltk.download('punkt')
nlp = spacy.load("en_core_web_sm")

skill_keywords = [
    "Python", "Golang", "Go", "AWS", "Java", "JavaScript", "React", "Node.js",
    "SQL", "MongoDB", "PostgreSQL", "Docker", "Kubernetes", "Git", "HTML", "CSS",
    "C++", "C#", "Linux", "Flask", "Django", "TensorFlow", "PyTorch", "Hadoop",
    "Spark", "Machine Learning", "Deep Learning", "REST API", "CI/CD", "Agile",
    "MySQL", "MongoDB", "GCP", "Azure", "Jenkins", "Ansible", "Terraform", "DevOps",
    "Matplotlib", "Plotly", "Front-end", "Back-end", "QT", "QML", "GUI",
    "Geographic Information System", "GIS", "FPGA", "OpenCV", "CUDA", "OpenCL", "Spacy",
    "NLTK", "Pandas", "NumPy", "Scikit-learn", "Keras", "FastAPI", "GraphQL", "NLP"
]

qualification_keywords = [
    'BTech', 'MTech', 'MCA', 'BCA', 'B.Sc', 'M.Sc', 'Bachelor', 'Master', 'Graduate',
    'Post Graduate', 'PHD', 'Computer Science', 'Engineering', 'Computer Application'
]

# Step 1: Extract text
def extract_text_from_pdf(path):
    text = ''
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n'
    return text

# Step 2: Remove summary section (heuristically)
def remove_summary_sections(text):
    summary_keywords = ['summary', 'about', 'overview', 'objective']
    lines = text.splitlines()
    clean_lines = []
    skip = False
    for line in lines:
        lower = line.strip().lower()
        if any(k in lower for k in summary_keywords):
            skip = True
            continue
        if skip and (line.strip() == '' or line.strip().lower() in ['skills', 'education', 'experience', 'projects']):
            skip = False
            continue
        if not skip:
            clean_lines.append(line)
    return '\n'.join(clean_lines)

# Step 3: Guess name
def guess_name_from_text(lines):
    exclude = ['email', 'resume', 'linkedin', 'github', 'portfolio', 'phone', 'contact']
    temp=[]
    for line in lines[:10]:
        clean = line.strip()
        if clean and clean.replace(" ", "").isalpha():
            if not any(word in clean.lower() for word in exclude):
                temp.extend(clean.split(" "))
                print(temp)
                if len(temp)>=2:
                  clean=""
                  for word in temp:
                    clean+=str(word)+" "
                  return clean.title()
    return None

# Step 4: Calculate experience from date ranges
def calculate_experience_from_ranges(text):
    # Match date ranges like "April 2024 - May 2024", "Jan 2022 to Jun 2022", etc.
    date_range_pattern = re.findall(r'([A-Za-z]{3,9})\s+(\d{4})\s*(?:-|to)\s*([A-Za-z]{3,9})\s+(\d{4})', text)
    total_months = 0
    month_map = {
        'january':1, 'february':2, 'march':3, 'april':4, 'may':5, 'june':6,
        'july':7, 'august':8, 'september':9, 'october':10, 'november':11, 'december':12
    }

    for start_month, start_year, end_month, end_year in date_range_pattern:
        try:
            sm = month_map[start_month.lower()]
            em = month_map[end_month.lower()]
            sy = int(start_year)
            ey = int(end_year)
            months = (ey - sy) * 12 + (em - sm)
            if months > 0:
                total_months += months
        except:
            continue

    if total_months == 0:
        return None
    if total_months >= 12:
        years = total_months // 12
        months = total_months % 12
        return f"{years} years" + (f" {months} months" if months else "")
    else:
        return f"{total_months} months"

# Step 5: Final extraction
def extract_resume_info(text):
    # Remove summary/overview section
    text = remove_summary_sections(text)

    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text_lower = text.lower()

    # Name
    name = guess_name_from_text(lines)

    # Skills
    found_skills = set()
    for skill in skill_keywords:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            found_skills.add(skill)

    # Qualification
    found_qualifications = set()
    for qual in qualification_keywords:
        if re.search(r'\b' + re.escape(qual.lower()) + r'\b', text_lower):
            found_qualifications.add(qual)

    # Experience (only from date ranges)
    experience = calculate_experience_from_ranges(text)

    return {
        'Name': name,
        'Skills': sorted(found_skills),
        'Qualification': sorted(found_qualifications),
        'Experience': experience
    }

# Run
if __name__ == "__main__":
    pdf_path = "ANIKET ROY Resume.pdf"
    raw_text = extract_text_from_pdf(pdf_path)
    info = extract_resume_info(raw_text)
    print("Extracted Resume Information:")
    print(f"Name: {info['Name']}")
    print(f"Skills: {', '.join(info['Skills']) if info['Skills'] else 'None'}")
    print(f"Qualification: {', '.join(info['Qualification']) if info['Qualification'] else 'None'}")
    print(f"Experience: {info['Experience'] if info['Experience'] else 'None'}")