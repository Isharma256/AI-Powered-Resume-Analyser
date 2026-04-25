from flask import Flask, render_template, request
import pdfplumber
import re

app = Flask(__name__)

LANGUAGES = ["python", "java", "c", "c++", "javascript", "html", "css"]
SKILLS = ["machine learning", "ai", "data analysis", "flask", "django", "react"]

def extract_text(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text.lower()

# 🔹 Extract CGPA
def extract_cgpa(text):
    match = re.search(r'(\d\.\d)', text)
    return match.group(1) if match else None

# 🔹 Analyze
def analyze(text):
    languages = [l for l in LANGUAGES if l in text]
    skills = [s for s in SKILLS if s in text]

    has_project = "project" in text
    has_edu = "education" in text
    has_cert = "certif" in text
    cgpa = extract_cgpa(text)

    score = 0
    score += min(len(languages) * 5, 15)
    score += min(len(skills) * 4, 25)

    if has_project:
        if any(word in text for word in LANGUAGES + SKILLS):
            score += 25
            project_type = "Technical Project"
        else:
            score += 10
            project_type = "Non-Technical Project"
    else:
        project_type = "Missing"

    if has_edu:
        score += 10
    if has_cert:
        score += 10

    if cgpa:
        val = float(cgpa)
        if val >= 8.5:
            score += 10
        elif val >= 7:
            score += 7
        else:
            score += 4

    score = min(score, 100)

    # 🔹 Feedback
    feedback = []

    if not has_project:
        feedback.append("Add a Projects section with technical details.")
    else:
        feedback.append("Projects section is present.")

    if not has_cert:
        feedback.append("Add certifications to improve your profile.")

    if not cgpa:
        feedback.append("Mention your CGPA or marks.")

    if len(skills) < 3:
        feedback.append("Add more relevant skills.")

    if len(languages) < 2:
        feedback.append("Include more programming languages.")

    return {
        "languages": languages,
        "skills": skills,
        "score": score,
        "project": project_type,
        "certificate": "Present" if has_cert else "Missing",
        "cgpa": cgpa if cgpa else "Missing",
        "education": "Present" if has_edu else "Missing",
        "feedback": feedback
    }

@app.route("/", methods=["GET", "POST"])
def home():
    result = None

    if request.method == "POST":
        file = request.files["resume"]

        if file and file.filename.endswith(".pdf"):
            text = extract_text(file)
            result = analyze(text)
        else:
            result = {"error": "Upload PDF only"}

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)