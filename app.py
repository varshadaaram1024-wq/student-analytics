from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

app = Flask(__name__)
app.secret_key = "studentanalytics"

# ---------------- DATASET ----------------
data = pd.read_excel("Updated_Student_Performance_Data1.xlsx", engine="openpyxl")

data["Total"] = data["Math"] + data["Programming"] + data["Communication"]

def performance(total):
    if total >= 240:
        return "High Performer"
    elif total >= 180:
        return "Average Performer"
    else:
        return "Low Performer"

data["Performance"] = data["Total"].apply(performance)

# ---------------- ML MODEL ----------------
X = data[["Math", "Programming", "Communication"]]
y = data["Performance"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = DecisionTreeClassifier()
model.fit(X_train, y_train)

# ---------------- ROUTES ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["username"] == "admin" and request.form["password"] == "1234":
            session["admin"] = True
            return redirect(url_for("admin"))
    return render_template("login.html")

@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect(url_for("login"))
    return render_template("admin.html")

@app.route("/students")
def students():
    return render_template("students.html", students=data.to_dict(orient="records"))

@app.route("/topstudents")
def topstudents():
    top = data.sort_values(by="Total", ascending=False).head(5)
    return render_template("topstudents.html", students=top.to_dict(orient="records"))

@app.route("/weakstudents")
def weakstudents():
    weak = data.sort_values(by="Total").head(5)
    return render_template("weakstudents.html", students=weak.to_dict(orient="records"))

# ---------------- PREDICTION ----------------

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    career = None
    suggestions = []
    skill = None
    performance_result = None
    learning_path = []
    roadmap = []

    if request.method == "POST":

        math = int(request.form["math"])
        prog = int(request.form["programming"])
        comm = int(request.form["communication"])
        interest = request.form["interest"]

        prediction = model.predict([[math, prog, comm]])
        performance_result = prediction[0]

        avg = (math + prog + comm) / 3

        if avg >= 80:
            skill = "Excellent Skill Level"
        elif avg >= 60:
            skill = "Moderate Skill Level"
        else:
            skill = "Needs Skill Improvement"

        # Career logic
        if interest == "Not Sure":
            career = "Interest Not Clear Yet"
            suggestions += [
                "Explore different fields",
                "Attend workshops",
                "Try mini projects",
                "Seek mentor guidance"
            ]

        elif interest == "AI" and prog >= 75 and math >= 75:
            career = "Recommended Career: Artificial Intelligence"

        elif interest == "Software" and prog >= 70:
            career = "Recommended Career: Software Development"

        elif interest == "Electronics" and math >= 70:
            career = "Recommended Career: Electronics"

        elif interest == "Management" and comm >= 70:
            career = "Recommended Career: Management"

        else:
            career = "Improve skills to decide career"

        # Suggestions
        if math < 60:
            suggestions.append("Improve math skills")
        if prog < 60:
            suggestions.append("Practice programming")
        if comm < 60:
            suggestions.append("Improve communication")

        # Learning Path
        if "Software" in str(career):
            learning_path = ["Learn Python", "Practice coding", "Build projects"]

        elif "Artificial Intelligence" in str(career):
            learning_path = ["Learn Python", "Study ML", "Work with datasets"]

        elif "Electronics" in str(career):
            learning_path = ["Learn basics", "Do hardware projects"]

        elif "Management" in str(career):
            learning_path = ["Improve communication", "Learn business"]

        if interest == "Not Sure":
            learning_path = ["Explore fields", "Try projects", "Attend workshops"]

        # ---------------- CAREER ROADMAP ----------------
        if "Software" in str(career):
            roadmap = [
                "Learn Python or Java",
                "Practice Data Structures",
                "Build projects",
                "Participate in coding contests",
                "Apply for internships"
            ]

        elif "Artificial Intelligence" in str(career):
            roadmap = [
                "Learn Python",
                "Study Machine Learning",
                "Work with datasets",
                "Learn AI tools",
                "Do internships"
            ]

        elif "Electronics" in str(career):
            roadmap = [
                "Learn electronics basics",
                "Work on Arduino",
                "Build hardware projects",
                "Understand embedded systems",
                "Apply for internships"
            ]

        elif "Management" in str(career):
            roadmap = [
                "Improve communication",
                "Learn business concepts",
                "Participate in discussions",
                "Take leadership roles",
                "Apply for internships"
            ]

        if interest == "Not Sure":
            roadmap = [
                "Explore different careers",
                "Attend workshops",
                "Try different projects",
                "Talk to mentors",
                "Find your interest"
            ]

    return render_template(
        "prediction.html",
        career=career,
        suggestions=suggestions,
        skill=skill,
        performance_result=performance_result,
        learning_path=learning_path,
        roadmap=roadmap
    )

# ---------------- LEARNING ----------------

@app.route("/learning")
def learning():
    modules = {
        "Programming": [
            {"title": "Python Basics", "link": "https://www.youtube.com/watch?v=_uQrJ0TkZlc"}
        ],
        "Mathematics": [
            {"title": "Algebra Basics", "link": "https://www.youtube.com/watch?v=grnP3mduZkM"}
        ],
        "Communication": [
            {"title": "Communication Skills", "link": "https://www.youtube.com/watch?v=HAnw168huqA"}
        ]
    }
    return render_template("learning.html", modules=modules)

# ---------------- QUIZ ----------------

@app.route("/quiz", methods=["GET", "POST"])
def quiz():

    subject = None
    score = None

    questions = {
        "programming": [
            ("Which language is used in ML?", "a", ["Python", "HTML"]),
            ("What is loop?", "a", ["Repeat code", "Stop code"]),
            ("Which is language?", "a", ["Python", "Google"]),
            ("Variable is?", "a", ["Stores data", "Deletes data"]),
            ("Python is?", "a", ["Language", "Browser"]),
            ("IDE used for?", "a", ["Coding", "Eating"]),
            ("2+2 output?", "a", ["4", "22"]),
            ("Comment symbol?", "a", ["#", "//"])
        ],
        "math": [
            ("5x6?", "a", ["30", "25"]),
            ("Square of 4?", "a", ["16", "8"]),
            ("10/2?", "a", ["5", "2"]),
            ("7+3?", "a", ["10", "9"]),
            ("9-4?", "a", ["5", "6"]),
            ("2^2?", "a", ["4", "2"]),
            ("12+8?", "a", ["20", "18"]),
            ("6x3?", "a", ["18", "15"])
        ],
        "communication": [
            ("Helps in?", "a", ["Presentation", "Sleep"]),
            ("Improves?", "a", ["Teamwork", "Lazy"]),
            ("Speaking skill?", "a", ["Important", "No"]),
            ("Confidence from?", "a", ["Practice", "Fear"]),
            ("Listening helps?", "a", ["Understand", "Confuse"]),
            ("Body language?", "a", ["Important", "No"]),
            ("Eye contact?", "a", ["Confidence", "Fear"]),
            ("Clear speech?", "a", ["Good", "Bad"])
        ]
    }

    if request.method == "POST":
        subject = request.form.get("subject")

        if request.form.get("q1"):
            score = 0
            for i in range(1, 9):
                if request.form.get(f"q{i}") == "a":
                    score += 1

    return render_template(
        "quiz.html",
        subject=subject,
        questions=questions.get(subject),
        score=score
    )

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)