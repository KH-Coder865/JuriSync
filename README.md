## ⚖️ Features
- **User & Lawyer Login:** Role-based authentication and dashboards.
- **Case Management:** Lawyers can add, view, and manage detailed legal cases.
- **Case Search:** Search cases by section, article, or type.
- **Lawyer Search:** Users can find lawyers by specialization and contact them.
- **Smart Case Prioritization:** Cases are ranked by urgency, complexity, and risk factors, helping in fast and effective case solving, reducing case backlogs.
- **AI Legal Chatbot:** Instant legal advice powered by Groq's LLaMA AI model.
- **Dashboard Analytics:** Track total, solved, and pending cases.
- **Secure Session Handling:** Protected Access to Features.

---

## 🚀 Technical Stack

This project utilizes the following technologies:

- **Backend**: Flask (lightweight Python framework)
- **Database**: SQLAlchemy (ORM for database management)
- **User Authentication**: Flask-Login (user session and auth management)
- **AI/Chat Bot**: GROQ (real-time Legal Assistance)
- **Frontend**: HTML/CSS, Bootstrap (responsive web design)
- **Environment**: Python venv (isolated environments for dependencies)
- **Version Control**: Git & GitHub

### 🔧 Libraries:
- Flask-SQLAlchemy, Flask-WTF, Jinja2, Werkzeug
  
### 🛠 Tools:
- **IDE**: Visual Studio Code
- **API Testing**: Postman

### 📦 Package Management:
- **Pip**: Install dependencies from `dependencies.txt`


## 💻 Setup Instructions

#### 1. **Install Python**
To run this project, you’ll need to have *Python 3.7+* installed on your system.

-n, make sure to check the box to *Add Python to PATH*.

- **Windows**: [Download Python](https://www.python.org/downloads/) and check *Add Python to PATH*.
- **macOS**: `brew install python`
- **Linux**: `sudo apt install python3`
    

  To confirm Python is installed, run this in your terminal:
  ```bash
  python --version
  ```
  
#### 2. **Clone the repository**
```bash
  -git clone https://github.com/KH-Coder865/JuriSync.git
  -cd JuriSync-main
```
#### 3. **Set Up a Virtual Environment**

A *virtual environment* is recommended to keep project dependencies isolated.

1. *Create a Virtual Environment:*

   In your project’s root directory, run the following command to create the virtual environment:
   
   ```bash
   python -m venv venv
   ```
   

   This will create a venv directory where the isolated Python environment will reside.

2. *Activate the Virtual Environment:*

   - *Windows:*
    ``` bash
     venv\Scripts\activate
    ```
     
   - *macOS/Linux:*
    ``` bash
     source venv/bin/activate
    ```
     
   After activation, your terminal prompt should change to something like:
   ``` bash
   (venv) $
   ```
   
#### 4. **Install Dependencies**

```bash
pip install -r requirements.txt
```

#### 5. **Run the Project**

```bash
python main.py
```

The app should now be running.

---

