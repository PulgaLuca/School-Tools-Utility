# Student Python Script Evaluation

## Overview

This project automatically tests and grades Python scripts submitted by students.
Each student has a personal folder containing one or more `.py` files.
The program executes each script, compares its output to the expected output, and generates an Excel report showing which exercises are correct, incorrect, or failed to run.

---

## Folder Structure

```
project/
├── evaluate_students.py
├── README.md
└── ALUMNI/
    ├── STUDENT_0/
    │   ├── exercise1.py
    │   ├── exercise2.py
    ├── STUDENT_1/
    │   ├── exercise1.py
    │   ├── exercise2.py
```

* Each subfolder inside **ALUMNI/** represents a student.
* Each student folder contains the Python scripts to be tested.

---

## Configuration

In the file `evaluate_students.py`, you can customize:

```python
base_dir = "ALUMNI"  # path to the folder containing all student folders

expected_outputs = {
    "exercise1.py": "Hello World\n",
    "exercise2.py": "42\n"
}

max_score = 1  # score assigned for each correct exercise
```

* `expected_outputs`: dictionary defining the correct expected output for each script name.
* `max_score`: number of points assigned for a correct result.

---

## How It Works

1. The script loops through all student folders in the `ALUMNI/` directory.
2. For each `.py` file:

   * The script is executed with a 5-second timeout.
   * Its standard output (`stdout`) is captured.
   * The result is compared to the expected output.
3. The results are collected in a table, including:

   * Student name
   * Script name
   * Actual output
   * Expected output
   * Status (correct, incorrect, timeout, or error)
   * Score (1 or 0)
4. A final Excel file is generated with two sheets:

   * **Details** — all exercises and results
   * **Summary** — total score per student

---

## Output Example

**Excel file:** `student_output_check.xlsx`

### Sheet 1: *Details*

| Student      | Script       | Actual Output | Expected Output | Result    | Score |
| ------------ | ------------ | ------------- | --------------- | --------- | ----- |
| Rossi Mario  | exercise1.py | Hello World   | Hello World     | correct   | 1     |
| Rossi Mario  | exercise2.py | 42            | 42              | correct   | 1     |
| Bianchi Anna | exercise2.py | 43            | 42              | incorrect | 0     |

### Sheet 2: *Summary*

| Student      | Total |
| ------------ | ----- |
| Rossi Mario  | 2     |
| Bianchi Anna | 0     |

---

## Error Handling

* **Incorrect** — The output does not match the expected output.
* **Timeout** — The script took more than 5 seconds to complete.
* **Error** — The script raised a Python exception (e.g., syntax error).
* **Expected output not defined** — The exercise was not found in the `expected_outputs` dictionary.

---

## Requirements

* Python 3.8 or later
* The following Python packages:

  ```bash
  pip install pandas openpyxl
  ```

---

## Running the Script

From the project directory, run:

```bash
python evaluate_students.py
```

After execution, an Excel file named **`student_output_check.xlsx`** will be created in the same directory.

---

## Customization

* You can add more exercises by updating the `expected_outputs` dictionary.
* You can change the timeout duration in the `subprocess.run()` call.
* You can assign different scores to each exercise by using a dictionary instead of a single `max_score`.
