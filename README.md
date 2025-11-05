# Classroom Automation Toolkit

This repository contains tools to **automate the management and evaluation of student assignments**.
It includes two main scripts:

---

## 1. Classroom Downloader

Automatically downloads homework submissions from **Google Classroom**, organises them into folders by class and assignment, and generates an Excel report with submission status.

**Main features**

* Download all attachments for a specific assignment
* Automatically create organised folder structures
* Generate an Excel report of submission status
* Secure authentication with Google API (OAuth 2.0)

**Quick start**

```bash
pip install -r requirements.txt
python main.py
```

Configure your Google credentials (`credentials.json`) and set:

```python
course_name = "Class Name"
coursework_name = "Assignment Name"
```

---

## 2. Student Script Evaluation

Automatically runs and grades students’ **Python scripts** stored in individual folders.
The program executes each `.py` file, compares its output to the expected one, and produces an Excel report with results and total scores.

**Main features**

* Run each student’s script automatically
* Compare outputs to expected results
* Assign scores and generate a grading Excel file

Run:

```bash
python evaluate_students.py
```

---

## Requirements

* Python 3.8 or later
* Packages: `pandas`, `openpyxl`, `google-api-python-client`, `google-auth-oauthlib`

---

For more detailed setup and configuration instructions, **read the README inside each project folder**.
