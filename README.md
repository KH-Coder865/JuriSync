## 🚀 Technical Stack

This project utilizes the following technologies:

### 1. **Backend Framework:**
- **Flask**: A lightweight Python web framework, perfect for building web applications. It's fast, simple, and flexible, making it an ideal choice for this project.

### 2. **Database:**
- **SQLAlchemy**: An Object-Relational Mapping (ORM) library that provides a high-level interface for interacting with relational databases. It helps to easily manage the database schema and execute SQL queries.

### 3. **User Authentication:**
- **Flask-Login**: A Flask extension used to manage user sessions, login, and authentication, ensuring secure user management.

### 4. **AI/Complexity Analysis:**
- **GROQ**: A Python library used for querying data with Grok language, enabling real-time complexity and urgency analysis of legal cases.

### 5. **Frontend:**
- **HTML/CSS**: The basic building blocks for creating the structure and styling of web pages.
- **Bootstrap**: A front-end framework that provides pre-designed components and layouts, ensuring responsive and mobile-first web design.

### 6. **Environment Management:**
- **Python venv (Virtual Environment)**: Creates isolated environments for the project, ensuring all dependencies are installed without interfering with the global Python installation.

### 7. **Version Control:**
- **Git & GitHub**: Version control systems that manage code changes and allow for easy collaboration via GitHub repositories.

### 🔧 Additional Tools and Libraries:
- **Flask-SQLAlchemy**: For ORM-based database interaction.
- **Flask-WTF**: For handling and validating forms in Flask applications.
- **Jinja2**: A templating engine for rendering HTML templates in Flask.
- **Werkzeug**: A WSGI utility library, providing HTTP-related functionality used internally by Flask.

---

### 🛠 Development Tools:
- **Visual Studio Code** (or your preferred IDE): Used for writing and debugging code.
- **Postman**: For testing APIs and sending requests during development.

---

### 📦 Package Management:
- **Pip**: Python's package installer, used to install dependencies from `requirements.txt`.

---

### 💻 Setup Instructions

#### 1. **Install Python**
To run this project, you’ll need to have *Python 3.7+* installed on your system.

- *Windows:*  
  - Download and install Python from [python.org/downloads](https://www.python.org/downloads/).
  - During installation, make sure to check the box to *Add Python to PATH*.

- *macOS/Linux:*  
  Python is likely pre-installed, but you can also install it via *Homebrew* (macOS) or *apt* (Linux):
  
  - *macOS:*
    bash
    brew install python
    
  - *Ubuntu/Debian:*
    bash
    sudo apt update
    sudo apt install python3
    

  To confirm Python is installed, run this in your terminal:
  bash
  python --version
  

---
####2. **Clone the repository**
```bash
  -git clone https://github.com/KH-Coder865/JuriSync.git
  -cd JuriSync-main
```

#### 2. **Set Up a Virtual Environment**

A *virtual environment* is recommended to keep project dependencies isolated.

1. *Create a Virtual Environment:*

   In your project’s root directory, run the following command to create the virtual environment:
   
   bash
   python -m venv venv
   

   This will create a venv directory where the isolated Python environment will reside.

2. *Activate the Virtual Environment:*

   - *Windows:*
     bash
     venv\Scripts\activate
     

   - *macOS/Linux:*
     bash
     source venv/bin/activate
     

   After activation, your terminal prompt should change to something like:
   bash
   (venv) $
   

---

#### 3. **Install Dependencies**

Now that the virtual environment is active, install all the project dependencies by running:

bash
pip install -r requirements.txt


This will install the libraries listed in the requirements.txt file.

---

#### 4. **Run the Project**

Once everything is set up, you can run the app with the following command (if it’s a Flask app, for example):

bash
python main.py


The app should now be running locally on http://127.0.0.1:5000/.

---


re structure this so that this looks minimilastic and appealing
