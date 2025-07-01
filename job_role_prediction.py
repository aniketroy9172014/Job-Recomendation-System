import warnings
warnings.filterwarnings("ignore")

import joblib
import pandas as pd
import re

# Load saved models and encoders
model = joblib.load('models\model.pkl')
mlb = joblib.load('models\mlb_skills.pkl')
degree_encoder = joblib.load('models\degree_encoder.pkl')
domain_encoder = joblib.load('models\domain_encoder.pkl')
job_encoder = joblib.load('models\job_encoder.pkl')

# ---- Preprocess Skills ----
def preprocess_skills(skills_input):
    skills_input_cleaned = [s.strip().lower() for s in skills_input]
    skills_vector = mlb.transform([skills_input_cleaned])
    skills_df_input = pd.DataFrame(skills_vector, columns=mlb.classes_)
    return skills_df_input



# ---- Preprocess Experience ----
def convert_experience(exp):
    if not exp:
        return 0
    exp = str(exp).lower().strip()

    # Handle common phrases
    if 'less than' in exp or 'few months' in exp:
        return 0.1
    if 'month' in exp:
        match = re.search(r'(\d+)', exp)
        if match:
            months = int(match.group(1))
            return round(months / 12, 2)  # convert to year fraction
        return 0.1

    # Handle range
    if '0-2' in exp: return 1
    if '2-5' in exp: return 3.5
    if '5+' in exp: return 6

    # Handle years like "1 year", "3 years"
    match = re.search(r'(\d+)', exp)
    if match:
        years = int(match.group(1))
        return years

    return 0  # default fallback



# ---- Preprocess Qualification ----
def extract_degree(qual):
    # Handle if qual is a list
    if isinstance(qual, list):
        qual = qual[0] if qual else ''
    qual = str(qual).lower()
    if 'phd' in qual: return 'PhD'
    elif 'm.sc' in qual or 'msc' in qual: return 'MSc'
    elif 'b.sc' in qual or 'bsc' in qual: return 'BSc'
    elif 'm.tech' in qual or 'mtech' in qual: return 'MTech'
    elif 'b.tech' in qual or 'btech' in qual: return 'BTech'
    else: return 'Other'

def extract_domain(qual):
    # Handle if qual is a list
    if isinstance(qual, list):
        qual = qual[0] if qual else ''
    qual = str(qual).lower()
    if 'cyber' in qual: return 'Cybersecurity'
    elif 'cloud' in qual: return 'Cloud'
    elif 'machine learning' in qual: return 'Machine Learning'
    elif 'data' in qual: return 'Data Science'
    elif 'computer' in qual or 'cs' in qual: return 'Computer Science'
    else: return 'General'


def predict_job_role(skills_input, experience_input, qualification_input):
    # ---- Preprocess Inputs ----
    skills_df_input = preprocess_skills(skills_input)

    experience_value = convert_experience(experience_input)

    degree = extract_degree(qualification_input)
    domain = extract_domain(qualification_input)

    degree_encoded = degree_encoder.transform([degree])[0]
    domain_encoded = domain_encoder.transform([domain])[0]

    # ---- Combine All Features ----
    input_df = skills_df_input.copy()
    input_df['Experience'] = experience_value
    input_df['Degree_encoded'] = degree_encoded
    input_df['Domain_encoded'] = domain_encoded

    # ---- Predict ----
    predicted_label = model.predict(input_df)[0]
    predicted_job_role = job_encoder.inverse_transform([predicted_label])[0]

    # print("✅ Predicted IT Job Role:", predicted_job_role)
    return predicted_job_role


if __name__ == "__main__":
    skills_input = ['HTML', 'CSS', 'JavaScript', 'EJS', 'Node.js', 'Express.js', 'Flask', 'PHP', 'Java', 'Python', 'C/C++', 'MongoDB', 'MySQL', 'Pandas', 'Scikit-Learn', 'Git', 'GitHub', 'MS Excel', 'Power BI']
    experience_input = '2 Year'
    qualification_input = 'B-tech'
    predicted_job_role = predict_job_role(skills_input, experience_input, qualification_input)
    print("Predicted Job Role:", predicted_job_role)