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

# def compute_urgency(case):
#     score = 0
#     if 'murder' in case.description.lower() or 'rape' in case.description.lower():
#         score += 5
#     if case.case_type.lower() in ['criminal']:
#         score += 3
#     if case.case_type.lower() in ['civil','property']:
#         score += 2
#     if (datetime.utcnow() - case.date_filed).days > 60:
#         score += 1
#     if case.status.lower() != 'solved':
#         score += 1
#     return min(score, 10)

def compute_urgency(case):
    score = 0.0

    # Weightage map (total possible = ~20, will normalize to 10)
    WEIGHTS = {
        'days_until_hearing': 3,
        'days_since_start': 2,
        'is_pil': 2,
        'minors_involved': 2,
        'risk_to_safety': 2,
        'people_influenced': 2,
        'is_repeated_offense': 1,
        'marginalized_group': 1,
        'economic_background': 2,
        'connected_to_larger_case': 1,
        'case_stage': 1,
        'complexity_level': 2,
        'case_type': 3,
        'domain':2,
        'section':2,
        'description':3,
    }

    # Imminent hearing = urgent
    if case.days_until_hearing is not None:
        if case.days_until_hearing <= 3:
            score += WEIGHTS['days_until_hearing']
        elif case.days_until_hearing <= 7:
            score += WEIGHTS['days_until_hearing'] * 0.75
        elif case.days_until_hearing <= 15:
            score += WEIGHTS['days_until_hearing'] * 0.5

    # Stalled/dragging cases
    if case.days_since_start is not None and case.days_since_start > 180:
        score += WEIGHTS['days_since_start']

    # Urgency based on IPC/CrPC section
    serious_sections = {
        '302': 1.0,  # Murder
        '376': 1.0,  # Rape
        '307': 0.8,  # Attempt to murder
        '498a': 0.7, # Domestic violence
        '354': 0.7,  # Assault on women
        '420': 0.5,  # Cheating
        '124a': 1.0, # Sedition
        '120b': 0.5, # Criminal conspiracy
        '395': 0.8,  # Dacoity
        '304b': 1.0, # Dowry death
        '363': 0.7,  # Kidnapping
    }

    section_code = case.section.strip().lower()
    if section_code in serious_sections:
        score += serious_sections[section_code] * 2  # Section gets max 2 weigh
    
    # Description-based urgency analysis
    description = case.description.lower()
    
    urgency_keywords = {
        'murder': 2.0,
        'rape': 2.0,
        'terrorism': 2.0,
        'life threatening': 1.5,
        'death': 1.5,
        'violence': 1.2,
        'assault': 1.2,
        'sexual harassment': 1.8,
        'child': 1.5,
        'urgent': 1.0,
        'emergency': 1.0,
        'immediate attention': 1.5,
        'custody': 1.2,
        'missing': 1.5,
        'mental health': 1.3,
        'blackmail': 1.0,
        'domestic abuse': 1.8,
        'acid attack': 2.0,
        'dowry': 1.5,
        'threat': 1.2,
        'kidnap': 1.8,
    }

    for keyword, weight in urgency_keywords.items():
        if keyword in description:
            score += WEIGHTS['description']

    # PILs are system-impacting
    if case.is_pil:
        score += WEIGHTS['is_pil']

    # Child safety = red alert
    if case.minors_involved:
        score += WEIGHTS['minors_involved']
    if case.risk_to_safety:
        score += WEIGHTS['risk_to_safety']

    #Domain
    if case.domain.lower() in ['international','national']:
        score+= WEIGHTS['domain']
    else:
        score+=1

    # People affected
    if case.people_influenced:
        if case.people_influenced >= 1000:
            score += WEIGHTS['people_influenced']
        elif case.people_influenced >= 100:
            score += WEIGHTS['people_influenced'] * 0.75
        elif case.people_influenced >= 10:
            score += WEIGHTS['people_influenced'] * 0.5

    if case.is_repeated_offense:
        score += WEIGHTS['is_repeated_offense']

    # Vulnerable communities
    marginalized_values = ['sc/st', 'obc', 'tribal', 'minority']
    if case.marginalized_group.lower() in marginalized_values:
        score += WEIGHTS['marginalized_group']

    poor_backgrounds = ['poor',  'bpl']
    if case.economic_background.lower() in poor_backgrounds:
        score += WEIGHTS['economic_background']
    elif case.economic_background.lower() in ['mc','umc']:
        score+=WEIGHTS['economic_background']-1
    else:
        score+=WEIGHTS['economic_background']-1.5

    if case.connected_to_larger_case:
        score += WEIGHTS['connected_to_larger_case']

    # Based on stage (example: 'investigation', 'trial', 'appeal', etc.)
    stage_urgency_map = {
        'trial': 0.95,
        'filing': 0.8,
        'drafting': 0.5,
        'pre-trial': 0.9,
        'appeal': 1.0
    }
    stage = case.case_stage.lower()
    if stage in stage_urgency_map:
        score += WEIGHTS['case_stage'] * stage_urgency_map[stage]

    # Complexity — urgent if complex and stuck
    complexity_map = {
        'high': 1.0,
        'medium': 0.6,
        'low': 0.3
    }
    level = case.complexity_level.lower()
    if level in complexity_map:
        score += WEIGHTS['complexity_level'] * complexity_map[level]

    # Certain domains are more urgent by nature
    high_priority_domains = ['criminal', 'family', 'human rights']
    if case.case_type.lower() in high_priority_domains:
        score += WEIGHTS['case_type']
    else:
        score+=1.5

    # Final normalization to 10
    urgency = min(round((score / 31.0) * 10), 10)
    return urgency

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_lawyer = db.Column(db.Boolean, default=False)
    specialization = db.Column(db.String(100),nullable=True)
    # yof=db.Column(db.Integer, nullable=True)
    # phone=db.Column(db.String(100),nullable=True)
    # email=db.Column(db.String(100),nullable=True)


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
    urgency = db.Column(db.Integer)

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
        specialization = str(request.form.get('specialization'))
        if specialization:
            lawyers = User.query.filter(
                User.is_lawyer == True,
                User.specialization.like(f'%{specialization}%')
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
        specialization = str(request.form.get('specialization'))
        
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
        for case in cases:
            case.urgency_score = compute_urgency(case)

    # Sort cases by urgency in descending order (fastest = Timsort)
        cases.sort(key=lambda c: c.urgency_score, reverse=True)
    else:
        cases = Case.query.all()
    return render_template('dashboard.html', cases=cases, compute_urgency=compute_urgency)

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     cases = Case.query.all()

#     # Annotate each case with its urgency score
#     for case in cases:
#         case.urgency_score = compute_urgency(case)

#     # Sort cases by urgency in descending order (fastest = Timsort)
#     cases.sort(key=lambda c: c.urgency_score, reverse=True)

#     return render_template('dashboard.html', cases=cases, compute_urgency=compute_urgency)

@app.route('/add_case', methods=['GET', 'POST'])
@login_required
def add_case():
    if not current_user.is_lawyer:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        new_case = Case(
            description=request.form['description'],
            case_type=str(request.form.get('case_type')),
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
            case_stage=request.form.get('case_stage'),
            is_pil=request.form.get('is_pil') == 'Yes',
            marginalized_group=request.form['marginalized_group'],
            is_repeated_offense=request.form.get('is_repeated_offense') == 'Yes',
            risk_to_safety=request.form.get('risk_to_safety') == 'Yes',
            minors_involved=request.form.get('minors_involved') == 'Yes',
            complexity_level=request.form['complexity_level']
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

# from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
# from datetime import datetime
# import groq
# import os

# app = Flask(__name__)
# f = open('C:/Users/KAUSHIK/Desktop/DOCS/KH/Groq_API_KEY.txt', 'r')
# groq_client = groq.Groq(api_key=f.readline())
# app.config['SECRET_KEY'] = 'your-secret-key'
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///legal.db'
# db = SQLAlchemy(app)
# login_manager = LoginManager(app)
# login_manager.login_view = 'login'

# class User(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(80), unique=True, nullable=False)
#     password = db.Column(db.String(120), nullable=False)
#     is_lawyer = db.Column(db.Boolean, default=False)
#     specialization = db.Column(db.String(100))

# class Case(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     description = db.Column(db.Text, nullable=False)
#     case_type = db.Column(db.String(100), nullable=False)
#     section = db.Column(db.String(50), nullable=False)
#     article = db.Column(db.String(50), nullable=False)
#     status = db.Column(db.String(20), default='Pending')
#     date_filed = db.Column(db.DateTime, default=datetime.utcnow)
#     lawyer_id = db.Column(db.Integer, db.ForeignKey('user.id'))

# @login_manager.user_loader
# def load_user(user_id):
#     return User.query.get(int(user_id))

# @app.route('/')
# def home():
#     return redirect(url_for('dashboard_stats'))

# @app.route('/dashboard-stats')
# def dashboard_stats():
#     total_cases = Case.query.count()
#     solved_cases = Case.query.filter_by(status='Solved').count()
#     pending_cases = Case.query.filter_by(status='Pending').count()
#     return render_template('index.html', total=total_cases, solved=solved_cases, pending=pending_cases)

# @app.route('/front', methods=['GET', 'POST'])
# def front():
#     if current_user.is_authenticated:
#         return redirect(url_for('search_lawyers'))
#     return render_template('front.html')

# @app.route('/search_lawyers', methods=['GET', 'POST'])
# @login_required
# def search_lawyers():
#     lawyers = []
#     if request.method == 'POST':
#         specialization = request.form.get('specialization', '')
#         if specialization:
#             lawyers = User.query.filter(
#                 User.is_lawyer == True,
#                 User.specialization.ilike(f'%{specialization}%')
#             ).all()
#         else:
#             lawyers = User.query.filter_by(is_lawyer=True).all()
#     return render_template('search_lawyers.html', lawyers=lawyers)

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         specialization = request.form['specialization']
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists')
#             return render_template('register.html')
#         new_user = User(
#             username=username,
#             password=password,
#             is_lawyer=True,
#             specialization=specialization
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful! Please login.')
#         return redirect(url_for('login'))
#     return render_template('register.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if current_user.is_authenticated:
#         return redirect(url_for('dashboard'))
#     if request.method == 'POST':
#         user = User.query.filter_by(username=request.form['username'], is_lawyer=True).first()
#         if user and user.password == request.form['password']:
#             login_user(user)
#             flash('Logged in successfully.')
#             return redirect(url_for('dashboard'))
#         flash('Invalid username or password')
#     return render_template('login.html')

# @app.route('/user_login', methods=['GET', 'POST'])
# def user_login():
#     if current_user.is_authenticated:
#         return redirect(url_for('search_lawyers'))
#     if request.method == 'POST':
#         user = User.query.filter_by(username=request.form['username'], is_lawyer=False).first()
#         if user and user.password == request.form['password']:
#             login_user(user)
#             flash('Logged in successfully.')
#             return redirect(url_for('search_lawyers'))
#         flash('Invalid username or password')
#     return render_template('user_login.html')

# @app.route('/user_register', methods=['GET', 'POST'])
# def user_register():
#     if current_user.is_authenticated:
#         return redirect(url_for('search_lawyers'))
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if User.query.filter_by(username=username).first():
#             flash('Username already exists')
#             return render_template('user_register.html')
#         new_user = User(
#             username=username,
#             password=password,
#             is_lawyer=False
#         )
#         db.session.add(new_user)
#         db.session.commit()
#         flash('Registration successful! Please login.')
#         return redirect(url_for('user_login'))
#     return render_template('user_register.html')

# @app.route('/logout')
# @login_required
# def logout():
#     logout_user()
#     return redirect(url_for('home'))

# # Urgency Scoring Logic
# def compute_urgency(case):
#     score = 0
#     if 'murder' in case.description.lower() or 'rape' in case.description.lower():
#         score += 5
#     if case.case_type.lower() in ['criminal', 'emergency']:
#         score += 3
#     if (datetime.utcnow() - case.date_filed).days > 60:
#         score += 1
#     if case.status.lower() != 'solved':
#         score += 1
#     return min(score, 10)

# @app.route('/dashboard')
# @login_required
# def dashboard():
#     if current_user.is_lawyer:
#         cases = Case.query.filter_by(lawyer_id=current_user.id).all()
#     else:
#         cases = Case.query.all()
#     return render_template('dashboard.html', cases=cases, compute_urgency=compute_urgency)

# @app.route('/add_case', methods=['GET', 'POST'])
# @login_required
# def add_case():
#     if not current_user.is_lawyer:
#         return redirect(url_for('dashboard'))
#     if request.method == 'POST':
#         new_case = Case(
#             description=request.form['description'],
#             case_type=request.form['case_type'],
#             section=request.form['section'],
#             article=request.form['article'],
#             lawyer_id=current_user.id
#         )
#         db.session.add(new_case)
#         db.session.commit()
#         return redirect(url_for('dashboard'))
#     return render_template('add_case.html')

# @app.route('/search', methods=['GET', 'POST'])
# @login_required
# def search():
#     if request.method == 'POST':
#         section = request.form.get('section', '')
#         article = request.form.get('article', '')
#         case_type = request.form.get('case_type', '')
#         query = Case.query
#         if section:
#             query = query.filter_by(section=section)
#         if article:
#             query = query.filter_by(article=article)
#         if case_type:
#             query = query.filter_by(case_type=case_type)
#         similar_cases = query.all()
#         return render_template('search.html', cases=similar_cases)
#     return render_template('search.html')

# @app.route('/contact_lawyer/<int:lawyer_id>')
# @login_required
# def contact_lawyer(lawyer_id):
#     lawyer = User.query.get_or_404(lawyer_id)
#     if not lawyer.is_lawyer:
#         flash('Invalid lawyer profile')
#         return redirect(url_for('search_lawyers'))
#     return render_template('contact_lawyer.html', lawyer=lawyer)

# @app.route('/chat', methods=['POST'])
# def chat():
#     message = request.json.get('message')
#     if not message:
#         return jsonify({'error': 'No message provided'}), 400
#     try:
#         chat_completion = groq_client.chat.completions.create(
#             model="meta-llama/llama-4-scout-17b-16e-instruct",
#             messages=[
#                 {
#                     "role": "system",
#                     "content": "You are a helpful legal assistant. Provide concise and accurate responses."
#                 },
#                 {
#                     "role": "user",
#                     "content": message
#                 }
#             ],
#             temperature=0.5,
#             max_tokens=1000
#         )
#         if chat_completion and chat_completion.choices and len(chat_completion.choices) > 0:
#             response = chat_completion.choices[0].message.content
#             return jsonify({'response': response})
#         else:
#             return jsonify({'error': 'No response from chat model'}), 500
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

# with app.app_context():
#     db.create_all()

# if __name__ == '_main_':
#     app.run(host='0.0.0.0', port=8080)

