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

