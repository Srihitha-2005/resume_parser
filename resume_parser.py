import os
import PyPDF2
import spacy
import re
# Load Spacy's English model
nlp = spacy.load('en_core_web_sm')
from docx import Document

# Common skills database (can be expanded)
SKILLS_DB = [
    'Python', 'Java', 'C++', 'C#', 'JavaScript', 'SQL', 'HTML', 'CSS',
    'Machine Learning', 'Deep Learning', 'Data Analysis', 'Data Science',
    'TensorFlow', 'PyTorch', 'Scikit-learn', 'Pandas', 'NumPy',
    'Django', 'Flask', 'React', 'Angular', 'Vue', 'Node.js',
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes',
    'Git', 'Linux', 'Windows', 'MacOS', 'Android', 'iOS',
    'REST API', 'GraphQL', 'MongoDB', 'PostgreSQL', 'MySQL',
    'Tableau', 'Power BI', 'Excel', 'JIRA', 'Agile', 'Scrum'
]

def extract_text_from_docx(docx_path):
    doc = Document(docx_path)
    text = ''
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
        return text

def extract_name(text):
    """
    Enhanced name extraction focusing on common resume patterns
    """
    # Get first 10 non-empty lines (more coverage than just 5)
    lines = [line.strip() for line in text.split('\n') if line.strip()][:10]
    
    # Common resume name patterns
    patterns = [
        r'^[A-Z][a-z]+(?: [A-Z][a-z]+)+$',  # First Last
        r'^[A-Z][a-z]+(?: [A-Z]\.? [A-Z][a-z]+)+$',  # First M. Last
        r'^[A-Z][A-Za-z]+(?: [A-Z][A-Za-z]+)+$',  # Allows all caps names
        r'^[A-Z][a-z]+ [A-Z][a-z]+(?: [A-Z][a-z]+)?$'  # 2-3 name parts
    ]
    
    # First pass: look for strict name matches
    for line in lines:
        # Skip lines with obvious non-name indicators
        if re.search(r'@|http|phone|resume|CV|linkedin|github|experience|skill|education|project', 
                    line, re.I):
            continue
            
        # Check against all patterns
        for pattern in patterns:
            if re.fullmatch(pattern, line):
                return line
    
    # Second pass: look for lines before email/phone
    for i, line in enumerate(lines):
        next_lines = lines[i+1:i+3]
        has_contact = any(re.search(r'@|\+?\d', nl) for nl in next_lines)
        
        if has_contact and not re.search(r'@|http|\d', line):
            # If next lines have contact info and current line doesn't, it's likely the name
            return line
    
    # Final fallback: return the first line that looks like a name
    for line in lines:
        words = line.split()
        if (2 <= len(words) <= 4 and 
            all(w[0].isupper() for w in words) and 
            not any(c.isdigit() for c in line)):
            return line
    
    return "Name Not Found"

def extract_email(text):
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.findall(email_pattern, text)

def extract_phone(text):
    phone_pattern = r"(?:\+?\d[\d\s\-().]{8,}\d)"
    matches = re.findall(phone_pattern, text)
    phones = []
    for match in matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) == 10 or (len(digits) == 12 and digits.startswith("91")):
            phones.append(match.strip())
    return phones if phones else ["N/A"]

def extract_skills(text):
    text = text.replace('\n', ' ')  # Remove newlines that could break word matches
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if re.search(r'\b' + re.escape(skill.lower()) + r'\b', text_lower):
            print(f"Matched skill: {skill}")  # Debugging line
            found_skills.append(skill)

    skill_patterns = [
        r'\b(?:machine learning|ml)\b',
        r'\b(?:deep learning|dl)\b',
        r'\b(?:natural language processing|nlp)\b',
        r'\b(?:computer vision|cv)\b',
        r'\b(?:artificial intelligence|ai)\b'
    ]

    for pattern in skill_patterns:
        matches = re.findall(pattern, text_lower)
        for match in matches:
            formatted_skill = ' '.join(word.capitalize() for word in match.split())
            if formatted_skill not in found_skills:
                print(f"Matched pattern skill: {formatted_skill}")  # Debugging line
                found_skills.append(formatted_skill)

    return list(set(found_skills))[:10]

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r') as file:
        return file.read()

def parse_resume(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    print(f"Processing file: {file_path}, Detected extension: {ext}")

    if ext == ".pdf":
        text = extract_text_from_pdf(file_path)
    elif ext == ".docx":
        text = extract_text_from_docx(file_path)
    elif ext == ".txt":
        text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    resume_data = {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'skills': extract_skills(text),
        'text': text  # Store the full text for BERT processing
    }
    return resume_data
