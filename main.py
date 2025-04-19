from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import groq
import os
from flask import jsonify

app = Flask(__name__)
f=open('C:/Users/KAUSHIK/Desktop/DOCS/KH/Groq_API_KEY.txt','r')
groq_client = groq.Groq(api_key=f.readline())
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///legal.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_lawyer = db.Column(db.Boolean, default=False)
    specialization = db.Column(db.String(100))

class Case(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)
    case_type = db.Column(db.String(100), nullable=False)
    section = db.Column(db.String(50), nullable=False)
    article = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    date_filed = db.Column(db.DateTime, default=datetime.utcnow)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    domain = db.Column(db.String(20), nullable=False)
    days_until_hearing = db.Column(db.Integer)
    days_since_start = db.Column(db.Integer)
    people_influenced = db.Column(db.Integer)
    economic_background = db.Column(db.String(100))
    connected_to_larger_case = db.Column(db.Boolean, default=False)
    previous_decisions = db.Column(db.Text, nullable=False)
    case_stage = db.Column(db.String(50), nullable=False)
    is_pil = db.Column(db.Boolean, default=False)
    marginalized_group = db.Column(db.String(50),nullable=False)
    is_repeated_offense = db.Column(db.Boolean, default=False)
    risk_to_safety = db.Column(db.Boolean, default=False)
    minors_involved = db.Column(db.Boolean, default=False)
    complexity_level = db.Column(db.String(20), nullable=False)
    urgency_level = db.Column(db.String(20), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return redirect(url_for('dashboard_stats'))

@app.route('/dashboard-stats')
def dashboard_stats():
    total_cases = Case.query.count()
    solved_cases = Case.query.filter_by(status='Solved').count()
    pending_cases = Case.query.filter_by(status='Pending').count()
    return render_template('index.html', total=total_cases, solved=solved_cases, pending=pending_cases)

@app.route('/front',methods=['GET', 'POST'])
def front():
    if current_user.is_authenticated:
        return redirect(url_for('search_lawyers'))
    return render_template('front.html')

@app.route('/search_lawyers', methods=['GET', 'POST'])
@login_required
def search_lawyers():
    lawyers = []
    if request.method == 'POST':
        specialization = request.form.get('specialization', '')
        if specialization:
            lawyers = User.query.filter(
                User.is_lawyer == True,
                User.specialization.ilike(f'%{specialization}%')
            ).all()
        else:
            lawyers = User.query.filter_by(is_lawyer=True).all()
    return render_template('search_lawyers.html', lawyers=lawyers)



@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        specialization = request.form['specialization']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
            
        new_user = User(
            username=username,
            password=password,
            is_lawyer=True,
            specialization=specialization
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], is_lawyer=True).first()
        if user and user.password == request.form['password']:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    if current_user.is_authenticated:
        return redirect(url_for('search_lawyers'))
        
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username'], is_lawyer=False).first()
        if user and user.password == request.form['password']:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('search_lawyers'))
        flash('Invalid username or password')
    return render_template('user_login.html')

@app.route('/user_register', methods=['GET', 'POST'])
def user_register():
    if current_user.is_authenticated:
        return redirect(url_for('search_lawyers'))
        
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('user_register.html')
            
        new_user = User(
            username=username,
            password=password,
            is_lawyer=False
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('user_login'))
    return render_template('user_register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.is_lawyer:
        cases = Case.query.filter_by(lawyer_id=current_user.id).all()
    else:
        cases = Case.query.all()
    return render_template('dashboard.html', cases=cases)

@app.route('/add_case', methods=['GET', 'POST'])
@login_required
def add_case():
    if not current_user.is_lawyer:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        new_case = Case(
            description=request.form['description'],
            case_type=request.form['case_type'],
            section=request.form['section'],
            status=request.form['status'],
            article=request.form['article'],
            lawyer_id=current_user.id,
            domain=request.form['domain'],
            days_until_hearing=int(request.form['days_until_hearing']),
            days_since_start=int(request.form['days_since_start']),
            people_influenced=int(request.form['people_influenced']),
            economic_background=request.form['economic_background'],
            connected_to_larger_case=request.form.get('connected_to_larger_case') == 'Yes',
            previous_decisions=request.form['previous_decisions'],
            case_stage=request.form['case_stage'],
            is_pil=request.form.get('is_pil') == 'Yes',
            marginalized_group=request.form['marginalized_group'],
            is_repeated_offense=request.form.get('is_repeated_offense') == 'Yes',
            risk_to_safety=request.form.get('risk_to_safety') == 'Yes',
            minors_involved=request.form.get('minors_involved') == 'Yes',
            complexity_level=request.form['complexity_level'],
            urgency_level=request.form['urgency_level']
        )
        db.session.add(new_case)
        db.session.commit()
        return redirect(url_for('dashboard'))
    return render_template('add_case.html')

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        section = request.form.get('section', '')
        article = request.form.get('article', '')
        case_type = request.form.get('case_type', '')
        
        query = Case.query
        if section:
            query = query.filter_by(section=section)
        if article:
            query = query.filter_by(article=article)
        if case_type:
            query = query.filter_by(case_type=case_type)
            
        similar_cases = query.all()
        return render_template('search.html', cases=similar_cases)
    return render_template('search.html')

with app.app_context():
    db.create_all()

@app.route('/contact_lawyer/<int:lawyer_id>')
@login_required
def contact_lawyer(lawyer_id):
    lawyer = User.query.get_or_404(lawyer_id)
    if not lawyer.is_lawyer:
        flash('Invalid lawyer profile')
        return redirect(url_for('search_lawyers'))
    return render_template('contact_lawyer.html', lawyer=lawyer)

@app.route('/chat', methods=['POST'])
def chat():
    message = request.json.get('message')
    if not message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        chat_completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful legal assistant. Provide concise and accurate responses."
                },
                {
                    "role": "user",
                    "content": message
                }
            ],
            temperature=0.5,
            max_tokens=1000
        )
        
        if chat_completion and chat_completion.choices and len(chat_completion.choices) > 0:
            response = chat_completion.choices[0].message.content
            return jsonify({'response': response})
        else:
            return jsonify({'error': 'No response from chat model'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
