

---

### Requirements

This project uses the following Python libraries:

* `pandas`
* `pyodbc`

Ensure that you have Python installed before proceeding.

### Installation

1. Navigate to the root directory of the project.
2. Install all required libraries using the provided `requirements.txt` file:

```
pip install -r requirements.txt
```

### Preparing Input Data

1. Place your CSV file inside the `input/` directory located in the project root.
2. Make sure the CSV file has the correct structure expected by the import script.

### Running the Import Process

From the project root, execute:

```
python main.py --import
```

This will start the import procedure using the CSV file located in the `input` directory.

---
