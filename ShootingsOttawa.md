# Ottawa Shooting Incidents Dashboard (2018-2024)

An interactive data visualization dashboard built with **Python Dash** to explore and analyze **shooting incidents in Ottawa, Canada from 2018 to 2023**. This project provides dynamic insights into yearly shooting trends, injury severity levels, and neighbourhood-based statistics, enabling stakeholders to better understand patterns of violence across the city.

## Project Overview

The Ottawa Shootings Dashboard is designed to transform raw incident data into an interactive web application where users can:

- View **yearly shooting statistics** with filters for injury levels (Fatal, Major, Minor, etc.).
- Analyze shooting events across Ottawa **neighbourhoods**.
- Toggle between **yearly trend charts** and **geospatial map visualizations**.
- Dynamically filter data through **dropdown menus and input fields**.

This dashboard is aimed at supporting **law enforcement agencies, policymakers, researchers, and community organizations** by providing a clear, data-driven view of gun-related incidents in Ottawa.

---

## Features

- **Interactive Dropdown Filters** to select statistics (Yearly or Map based).
- **Input Field for Year Selection** to view data for specific years (2018-2024).
- **Dynamic Graph Layouts**: Bar charts, line graphs, and map visualizations adjust based on user selections.
- **Responsive Design** using Flexbox to ensure charts are well-aligned and accessible across screen sizes.
- **Callback Functions** that manage component interactivity and conditional input field enabling/disabling.

---

## Technologies Used

- **Python**
  - Dash
  - Plotly Express
  - Pandas
  - MySQL Connector (for data retrieval)
- **MySQL**
  - Data aggregation and statistical queries
- **HTML/CSS** (inline Dash styling)
- **Jupyter Notebooks** (for data cleaning and exploratory analysis)

---

## File Structure

```
ottawa-shootings-dashboard/
├── app.py                # Main Dash Application File
├── data/
│   └── ottawa_shootings.csv  # Cleaned shooting incidents dataset
├── assets/
│   └── custom_styles.css     # Optional external CSS for styling (if needed)
├── notebooks/
│   └── data_cleaning.ipynb   # Jupyter Notebook for data preparation
└── README.md
```

---

## Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/yourusername/ottawa-shootings-dashboard.git
cd ottawa-shootings-dashboard
```

2. **Create a Virtual Environment & Install Dependencies**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Run the Dash App**

```bash
python app.py
```

Access the dashboard in your browser at: `http://127.0.0.1:8050/`

---

## Future Improvements

- Integrate a **live database connection** for real-time updates.
- Add **filterable map legends** and clustering for dense areas.
- Implement **user-driven report generation (PDF/CSV exports)**.
- Enhance **mobile responsiveness** for smaller screens.

---

## Project Author

**Olamide Olayinka**\
[LinkedIn](https://www.linkedin.com/in/yourprofile/)\
[Email: olamideolayinka@cmail.carleton.ca](mailto\:olamideolayinka@cmail.carleton.ca)

---

## License

This project is licensed under the MIT License.

---

## Acknowledgments

- Ottawa Police Service (for incident data)
- Open Data Ottawa Portal
- Plotly & Dash Documentation

---

## Screenshot



---

## Demo Video

Coming soon...

---

## ⭐ Star this repository if you found it useful!

