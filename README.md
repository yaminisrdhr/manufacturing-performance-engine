# Manufacturing Performance Engine

A Python-based manufacturing analytics application built with Streamlit to analyse production data, calculate manufacturing KPIs, and monitor operational performance.

## 1. Project Overview

Manufacturing operations generate large amounts of production data across machines, processes, and production shifts. However, this data often comes in different formats and structures, making performance analysis challenging.

The Manufacturing Performance Engine aims to simplify this process by allowing users to upload production datasets, map relevant data fields, process operational information, and calculate key manufacturing performance indicators.

## 2. Key Features

- Data Upload: Upload CSV and Excel production datasets.
- Worksheet Selection: Select individual worksheets from Excel workbooks.
- Data Preview: Inspect uploaded datasets before analysis.
- Column Mapping: Manually map dataset columns to standard manufacturing parameters.
- Data Quality Validation: Validate selected data fields before KPI calculations.
- Time Normalisation: Convert time measurements into a common unit (seconds).
- Dynamic Timestamp Processing: Detect matching start and end timestamp columns and generate duration columns automatically.
- Manufacturing KPI Calculation: Calculate key production and operational performance metrics.
- Interactive Dashboard: Display calculated manufacturing KPIs through a Streamlit interface.

## 3. Manufacturing KPIs

The application currently supports calculations for:

- Total Production Output
- Flow Rate
- Process Capacity
- Cycle Time
- Takt Time
- Idle Time
- Utilisation
- Overall Equipment Effectiveness (OEE)

Metric availability depends on the columns and information provided in the uploaded dataset.

## 4. Technology Stack

- Python
- Pandas
- Streamlit
- NumPy
- Regular Expressions
- Datetime Processing

## 5. Installation and Setup

Clone the repository:

bash
git clone https://github.com/yaminisrdhr/manufacturing-performance-engine.git

Navigate to the project directory:

bash
cd manufacturing-performance-engine

Install dependencies:

bash
pip install -r requirements.txt

Run the application:

bash
streamlit run app.py

The application will open in your browser.

## 6. Project Structure

manufacturing-performance-engine/
│
├── app.py
├── README.md
├── requirements.txt
├── .gitignore
│
└── screenshots/

## 7. Development Roadmap

The project is being developed incrementally.

Planned enhancements include:

- Intelligent column mapping using column semantics, data types, sample values, and dataset context.
- Confidence-based automatic field mapping.
- Improved support for different manufacturing dataset structures.
- Expanded manufacturing analytics and performance insights.

## 8. Project Status

**Version:** 0.1

The initial version includes data upload, manual column mapping, data validation, time normalisation, dynamic timestamp processing, manufacturing KPI calculations, and dashboard visualisation.

Intelligent column mapping is currently under development.

---

Note : Developed as a hands-on project exploring Python-based manufacturing analytics and digital manufacturing applications.
