from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)
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
    status = db.Column(db.String(20), default='Pending')
    date_filed = db.Column(db.DateTime, default=datetime.utcnow)
    lawyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    total_cases = Case.query.count()
    solved_cases = Case.query.filter_by(status='Solved').count()
    pending_cases = Case.query.filter_by(status='Pending').count()
    return render_template('index.html', total=total_cases, solved=solved_cases, pending=pending_cases)

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
        user = User.query.filter_by(username=request.form['username']).first()
        if user and user.password == request.form['password']:
            login_user(user)
            flash('Logged in successfully.')
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

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
            article=request.form['article'],
            lawyer_id=current_user.id
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)