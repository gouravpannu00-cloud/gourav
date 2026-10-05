"""
English Tutor Flask Application - Main Entry Point
"""
import os
import sys
import json
import re
import bcrypt
import jwt
import random
from datetime import datetime, timedelta, date
from functools import wraps

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///english_tutor.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])

db = SQLAlchemy(app)

print("English Tutor - Starting application...")


# ==================== DATABASE MODELS ====================

class User(db.Model):
    """User model for authentication and profile management."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    daily_goal_minutes = db.Column(db.Integer, default=30)
    streak_days = db.Column(db.Integer, default=0)
    last_active_date = db.Column(db.Date)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'daily_goal_minutes': self.daily_goal_minutes,
            'streak_days': self.streak_days,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Lesson(db.Model):
    """Lesson model for structured learning content."""
    __tablename__ = 'lessons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    difficulty = db.Column(db.String(20), default='beginner')
    order_index = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'content': self.content,
            'difficulty': self.difficulty,
            'order_index': self.order_index
        }


class UserProgress(db.Model):
    """Track user progress through lessons."""
    __tablename__ = 'user_progress'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Float, default=0)
    time_spent_minutes = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'lesson_id': self.lesson_id,
            'completed': self.completed,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'score': self.score,
            'time_spent_minutes': self.time_spent_minutes
        }


class Vocabulary(db.Model):
    """Technical vocabulary database."""
    __tablename__ = 'vocabulary'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.Text, nullable=False)
    example = db.Column(db.Text)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20), default='intermediate')

    def to_dict(self):
        return {
            'id': self.id,
            'word': self.word,
            'definition': self.definition,
            'example': self.example,
            'category': self.category,
            'difficulty': self.difficulty
        }


class UserVocabulary(db.Model):
    """Track user's vocabulary mastery."""
    __tablename__ = 'user_vocabulary'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vocab_id = db.Column(db.Integer, db.ForeignKey('vocabulary.id'), nullable=False)
    mastery_level = db.Column(db.Integer, default=0)
    times_reviewed = db.Column(db.Integer, default=0)
    last_reviewed = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'vocab_id': self.vocab_id,
            'mastery_level': self.mastery_level,
            'times_reviewed': self.times_reviewed
        }


class Quiz(db.Model):
    """Quiz model for assessments."""
    __tablename__ = 'quizzes'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    difficulty = db.Column(db.String(20), default='intermediate')

    questions = db.relationship('QuizQuestion', backref='quiz', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'difficulty': self.difficulty,
            'question_count': len(self.questions)
        }


class QuizQuestion(db.Model):
    """Individual quiz questions."""
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(30), nullable=False)
    options = db.Column(db.Text)
    correct_answer = db.Column(db.Text, nullable=False)
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'question_type': self.question_type,
            'options': json.loads(self.options) if self.options else [],
            'points': self.points
        }

    def to_dict_with_answer(self):
        data = self.to_dict()
        data['correct_answer'] = self.correct_answer
        data['explanation'] = self.explanation
        return data


class QuizAttempt(db.Model):
    """Record of quiz attempts."""
    __tablename__ = 'quiz_attempts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    answers = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'quiz_id': self.quiz_id,
            'score': self.score,
            'total_questions': self.total_questions,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class ChatHistory(db.Model):
    """AI tutor chat history."""
    __tablename__ = 'chat_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    tutor_response = db.Column(db.Text, nullable=False)
    corrections = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_message': self.user_message,
            'tutor_response': self.tutor_response,
            'corrections': json.loads(self.corrections) if self.corrections else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DailyActivity(db.Model):
    """Daily activity tracking for streaks."""
    __tablename__ = 'daily_activity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_date = db.Column(db.Date, nullable=False)
    minutes_active = db.Column(db.Integer, default=0)
    lessons_completed = db.Column(db.Integer, default=0)
    quizzes_completed = db.Column(db.Integer, default=0)
    words_learned = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'id': self.id,
            'activity_date': self.activity_date.isoformat() if self.activity_date else None,
            'minutes_active': self.minutes_active,
            'lessons_completed': self.lessons_completed,
            'quizzes_completed': self.quizzes_completed,
            'words_learned': self.words_learned
        }


class WritingSubmission(db.Model):
    """Writing practice submissions."""
    __tablename__ = 'writing_submissions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    submission = db.Column(db.Text, nullable=False)
    feedback = db.Column(db.Text)
    score = db.Column(db.Float)
    submission_type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'submission': self.submission,
            'feedback': self.feedback,
            'score': self.score,
            'submission_type': self.submission_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class SpeakingScenario(db.Model):
    """Speaking practice scenarios."""
    __tablename__ = 'speaking_scenarios'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    scenario = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20), default='intermediate')
    sample_response = db.Column(db.Text)
    tips = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'scenario': self.scenario,
            'category': self.category,
            'difficulty': self.difficulty,
            'sample_response': self.sample_response,
            'tips': self.tips
        }


class InterviewQuestion(db.Model):
    """Interview questions for developer roles."""
    __tablename__ = 'interview_questions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    sample_answer = db.Column(db.Text)
    tips = db.Column(db.Text)

    def to_dict(self):
        return {
            'id': self.id,
            'question': self.question,
            'category': self.category,
            'difficulty': self.difficulty,
            'sample_answer': self.sample_answer,
            'tips': self.tips
        }


class ReadingArticle(db.Model):
    """Reading practice articles."""
    __tablename__ = 'reading_articles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    difficulty = db.Column(db.String(20))
    word_count = db.Column(db.Integer)
    reading_time_minutes = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'difficulty': self.difficulty,
            'word_count': self.word_count,
            'reading_time_minutes': self.reading_time_minutes
        }


# ==================== HELPER FUNCTIONS ====================

def hash_password(password):
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password, password_hash):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def generate_token(user_id):
    """Generate JWT token for authenticated user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')


def decode_token(token):
    """Decode JWT token."""
    try:
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload['user_id']
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def token_required(f):
    """Decorator to protect routes with token authentication."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        try:
            token = token.replace('Bearer ', '')
            user_id = decode_token(token)
            if not user_id:
                return jsonify({'error': 'Token is invalid or expired'}), 401
        except Exception:
            return jsonify({'error': 'Token is invalid'}), 401
        return f(user_id, *args, **kwargs)
    return decorated


# ==================== AI TUTOR SERVICE ====================

class EnglishTutor:
    """AI-style English tutor that provides polite corrections."""

    GRAMMAR_PATTERNS = [
        {
            'pattern': r'\bi\b',
            'replacement': 'I',
            'explanation': 'The pronoun "I" should always be capitalized in English.'
        },
        {
            'pattern': r'\b(he|she|it)\s+have\b',
            'replacement': None,
            'explanation': 'Use "has" with he/she/it (third person singular).',
            'replacer': lambda m: m.group(1) + ' has'
        },
        {
            'pattern': r'\b(I|we|they|you)\s+has\b',
            'replacement': None,
            'explanation': 'Use "have" with I/we/they/you.',
            'replacer': lambda m: m.group(1) + ' have'
        },
        {
            'pattern': r'\balot\b',
            'replacement': 'a lot',
            'explanation': '"A lot" is always two words.'
        },
        {
            'pattern': r'\bcould of\b',
            'replacement': 'could have',
            'explanation': 'Use "could have" (not "could of").'
        },
        {
            'pattern': r'\bshould of\b',
            'replacement': 'should have',
            'explanation': 'Use "should have" (not "should of").'
        },
        {
            'pattern': r'\bwould of\b',
            'replacement': 'would have',
            'explanation': 'Use "would have" (not "would of").'
        },
        {
            'pattern': r'\btheir\s+(is|are|was|were)\b',
            'replacement': None,
            'explanation': 'Use "there is/are" for existence, not "their".',
            'replacer': lambda m: 'there ' + m.group(1)
        },
        {
            'pattern': r'\bme\s+and\s+(\w+)\b',
            'replacement': None,
            'explanation': 'Put others before yourself: "[Name] and I" (not "me and [name]").',
            'replacer': lambda m: m.group(1) + ' and I'
        },
    ]

    PROFESSIONAL_UPGRADES = {
        'i think': 'In my opinion',
        'i guess': 'I believe',
        'yeah': 'Yes',
        'yep': 'Yes',
        'nope': 'No',
        'gonna': 'going to',
        'wanna': 'want to',
        'gotta': 'have to',
        'kinda': 'kind of',
        'sorta': 'sort of',
        'dunno': "don't know",
        'lemme': 'let me',
        'gimme': 'give me',
        'asap': 'as soon as possible',
        'pls': 'please',
        'sry': 'sorry',
        'u': 'you',
        'r': 'are',
        'ur': 'your',
        'b4': 'before',
        'thx': 'thank you',
        'btw': 'by the way',
    }

    @staticmethod
    def analyze_message(message):
        """Analyze a message and return corrections."""
        corrections = []
        corrected = message

        # Apply grammar pattern corrections
        for rule in EnglishTutor.GRAMMAR_PATTERNS:
            pattern = re.compile(rule['pattern'], re.IGNORECASE)
            matches = list(pattern.finditer(corrected))
            for match in matches:
                original = match.group()
                if 'replacer' in rule and rule['replacer']:
                    try:
                        corrected_text = rule['replacer'](match)
                    except (IndexError, AttributeError):
                        corrected_text = rule.get('replacement', original)
                else:
                    corrected_text = rule.get('replacement', original)
                if original != corrected_text:
                    corrections.append({
                        'type': 'grammar',
                        'original': original,
                        'corrected': corrected_text,
                        'explanation': rule['explanation']
                    })
            if 'replacer' in rule and rule['replacer']:
                try:
                    corrected = pattern.sub(rule['replacer'], corrected)
                except (IndexError, AttributeError, re.error):
                    pass
            elif rule.get('replacement'):
                corrected = pattern.sub(rule['replacement'], corrected)

        # Apply professional language upgrades
        lower_msg = corrected.lower()
        for informal, formal in EnglishTutor.PROFESSIONAL_UPGRADES.items():
            if informal in lower_msg:
                corrections.append({
                    'type': 'professional',
                    'original': informal,
                    'corrected': formal,
                    'explanation': f'Consider using "{formal}" instead of "{informal}" in professional communication.'
                })
                # Use word boundary matching for replacements
                pattern = re.compile(r'\b' + re.escape(informal) + r'\b', re.IGNORECASE)
                corrected = pattern.sub(formal, corrected)

        # Check for capitalization at start
        if corrected and corrected[0].islower():
            corrections.append({
                'type': 'capitalization',
                'original': corrected[0],
                'corrected': corrected[0].upper(),
                'explanation': 'Start sentences with a capital letter.'
            })
            corrected = corrected[0].upper() + corrected[1:]

        # Check for missing punctuation at end
        if corrected and corrected[-1] not in '.!?':
            corrections.append({
                'type': 'punctuation',
                'original': '(missing punctuation)',
                'corrected': '.',
                'explanation': 'End sentences with appropriate punctuation.'
            })
            corrected = corrected + '.'

        return {
            'original': message,
            'corrected': corrected,
            'corrections': corrections,
            'has_errors': len(corrections) > 0
        }

    @staticmethod
    def generate_response(analysis):
        """Generate a polite tutor response based on analysis."""
        if not analysis['has_errors']:
            responses = [
                "Great job! Your sentence is grammatically correct and professionally appropriate.",
                "Well done! That is a clear and professional way to express your idea.",
                "Perfect! Your English is excellent here - no corrections needed.",
                "Excellent work! This sentence demonstrates strong professional communication skills.",
            ]
            return random.choice(responses)

        response_parts = ["Thank you for sharing! I noticed a few things we can improve:"]

        for i, correction in enumerate(analysis['corrections'], 1):
            response_parts.append(f"\n{i}. **{correction['type'].title()}**: {correction['explanation']}")

        response_parts.append(f"\n\n**Original**: {analysis['original']}")
        response_parts.append(f"\n**Corrected**: {analysis['corrected']}")

        has_informal = any(c['type'] == 'professional' for c in analysis['corrections'])
        if has_informal:
            response_parts.append("\n\n**Better professional version**: Consider using more formal language like 'I would appreciate it if you could...' instead of casual phrases.")

        response_parts.append("\n\nKeep practicing - you are making great progress!")

        return ''.join(response_parts)


# ==================== SEED DATA ====================

def seed_database():
    """Populate database with initial sample data."""
    if Vocabulary.query.first():
        return

    vocab_data = [
        {'word': 'API', 'definition': 'Application Programming Interface - a set of protocols for building and integrating application software.', 'example': 'We need to document the REST API before sharing it with the frontend team.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'Repository', 'definition': 'A central location where code and project files are stored and managed.', 'example': 'Please clone the repository from GitHub and create a new branch for your feature.', 'category': 'git', 'difficulty': 'beginner'},
        {'word': 'Commit', 'definition': 'A snapshot of changes made to the codebase, saved with a descriptive message.', 'example': 'Make sure to write clear commit messages so the team can understand what changed.', 'category': 'git', 'difficulty': 'beginner'},
        {'word': 'Deploy', 'definition': 'To release or push code updates to a production or staging environment.', 'example': 'We plan to deploy the new feature to production after the QA testing is complete.', 'category': 'devops', 'difficulty': 'intermediate'},
        {'word': 'Debugging', 'definition': 'The process of finding and fixing errors or bugs in code.', 'example': 'I spent the morning debugging the authentication module - it was a missing token validation.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'Framework', 'definition': 'A pre-built structure that provides a foundation for developing applications.', 'example': 'React is a popular JavaScript framework for building user interfaces.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'Endpoint', 'definition': 'A specific URL where an API can be accessed and interacts with the application.', 'example': 'The /users endpoint returns a list of all registered users in JSON format.', 'category': 'api', 'difficulty': 'intermediate'},
        {'word': 'Refactoring', 'definition': 'Restructuring existing code without changing its external behavior to improve readability.', 'example': 'We should refactor this function - it has grown too complex and hard to maintain.', 'category': 'general', 'difficulty': 'intermediate'},
        {'word': 'Pull Request', 'definition': 'A request to merge code changes from one branch to another, typically for code review.', 'example': 'I submitted a pull request for the new authentication feature - could you review it?', 'category': 'git', 'difficulty': 'beginner'},
        {'word': 'Merge Conflict', 'definition': 'A situation when Git cannot automatically resolve differences in code between commits.', 'example': 'We have a merge conflict in the package.json file that needs to be resolved manually.', 'category': 'git', 'difficulty': 'intermediate'},
        {'word': 'Agile', 'definition': 'A project management methodology emphasizing iterative development and collaboration.', 'example': 'Our team follows Agile methodology with two-week sprints and daily standups.', 'category': 'methodology', 'difficulty': 'intermediate'},
        {'word': 'Sprint', 'definition': 'A fixed time period (usually 1-4 weeks) during which specific work is completed.', 'example': 'We have three story points remaining in this sprint.', 'category': 'methodology', 'difficulty': 'intermediate'},
        {'word': 'Standup', 'definition': 'A brief daily meeting where team members share progress and blockers.', 'example': 'During standup, mention if you are blocked on any tasks.', 'category': 'communication', 'difficulty': 'beginner'},
        {'word': 'Code Review', 'definition': 'The systematic examination of source code to find and fix mistakes.', 'example': 'Code reviews help maintain code quality and share knowledge across the team.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'DevOps', 'definition': 'A set of practices combining software development and IT operations.', 'example': 'Our DevOps team manages the CI/CD pipeline and infrastructure.', 'category': 'devops', 'difficulty': 'intermediate'},
        {'word': 'Scalability', 'definition': 'The capability of a system to handle growing amounts of work.', 'example': 'We need to ensure our database architecture supports scalability.', 'category': 'architecture', 'difficulty': 'advanced'},
        {'word': 'Middleware', 'definition': 'Software that connects different applications or services.', 'example': 'We use middleware to authenticate requests before they reach the route handlers.', 'category': 'architecture', 'difficulty': 'advanced'},
        {'word': 'Cache', 'definition': 'A hardware or software component that stores data for faster access.', 'example': 'Implement caching to reduce database load and improve response times.', 'category': 'architecture', 'difficulty': 'intermediate'},
        {'word': 'Version Control', 'definition': 'A system that records changes to files over time so you can recall specific versions.', 'example': 'Git is the most popular version control system used by developers.', 'category': 'git', 'difficulty': 'beginner'},
        {'word': 'Frontend', 'definition': 'The client-side of an application that users interact with directly.', 'example': 'The frontend team is working on improving the user dashboard.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'Backend', 'definition': 'The server-side of an application that handles logic, database, and authentication.', 'example': 'We need to optimize the backend queries to reduce latency.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'Dependency', 'definition': 'An external library or package that your project requires to function.', 'example': 'Before running the app, install all dependencies using npm install.', 'category': 'general', 'difficulty': 'beginner'},
        {'word': 'Environment Variables', 'definition': 'Key-value pairs that configure the behavior of an application in different environments.', 'example': 'Store sensitive information like API keys in environment variables.', 'category': 'devops', 'difficulty': 'intermediate'},
        {'word': 'Rollback', 'definition': 'Reverting code or a deployment to a previous working state.', 'example': 'If the deployment fails, we can rollback to the previous stable version.', 'category': 'devops', 'difficulty': 'intermediate'},
    ]

    for vocab in vocab_data:
        db.session.add(Vocabulary(**vocab))

    lessons_data = [
        {'title': 'Writing Effective Emails', 'category': 'writing', 'difficulty': 'beginner', 'order_index': 1, 'content': '<h3>Writing Professional Emails</h3><p>Clear email communication is essential in the workplace.</p><h4>Subject Line</h4><ul><li>Be specific and concise</li><li>Include action items or deadlines</li></ul><h4>Structure</h4><ul><li>Greeting: "Hi [Name],"</li><li>Opening: State your purpose</li><li>Body: Provide details</li><li>Closing: Clear call to action</li><li>Sign-off: "Best regards,"</li></ul>'},
        {'title': 'Standup Updates', 'category': 'speaking', 'difficulty': 'beginner', 'order_index': 2, 'content': '<h3>Daily Standup Updates</h3><p>Answer three questions concisely:</p><ol><li>What did I accomplish yesterday?</li><li>What will I work on today?</li><li>Are there any blockers?</li></ol>'},
        {'title': 'Writing Bug Reports', 'category': 'writing', 'difficulty': 'intermediate', 'order_index': 3, 'content': '<h3>Writing Clear Bug Reports</h3><h4>Essential Elements</h4><ol><li><strong>Title:</strong> Be specific</li><li><strong>Steps to Reproduce:</strong> Numbered list</li><li><strong>Expected vs Actual:</strong> Clear comparison</li><li><strong>Environment:</strong> Browser, OS, etc.</li></ol>'},
        {'title': 'Grammar: Present Perfect', 'category': 'grammar', 'difficulty': 'intermediate', 'order_index': 4, 'content': '<h3>Present Perfect for Work Updates</h3><p>Structure: <strong>Subject + have/has + past participle</strong></p><ul><li>I <strong>have completed</strong> the task.</li><li>She <strong>has reviewed</strong> the code.</li></ul><p>Use for recent actions or unfinished time periods.</p>'},
        {'title': 'Pull Request Descriptions', 'category': 'writing', 'difficulty': 'intermediate', 'order_index': 5, 'content': '<h3>Writing PR Descriptions</h3><h4>Template</h4><pre>## Summary\n## Changes Made\n## Testing\n## Related Issues</pre>'},
        {'title': 'Grammar: Polite Questions', 'category': 'grammar', 'difficulty': 'beginner', 'order_index': 6, 'content': '<h3>Asking Questions Politely</h3><ul><li>"Could you please...?"</li><li>"Would you mind...?"</li><li>"I was wondering if you could...?"</li><li>"Would it be possible to...?"</li></ul>'},
    ]

    for lesson in lessons_data:
        db.session.add(Lesson(**lesson))

    quiz1 = Quiz(title='Technical Vocabulary Basics', category='vocabulary', difficulty='beginner')
    db.session.add(quiz1)
    db.session.flush()

    questions_data = [
        {'quiz_id': quiz1.id, 'question': 'What does API stand for?', 'question_type': 'multiple_choice', 'options': json.dumps(['Application Programming Interface', 'Advanced Program Integration', 'Application Process Internet', 'Automated Programming Interface']), 'correct_answer': 'Application Programming Interface', 'explanation': 'API stands for Application Programming Interface.'},
        {'quiz_id': quiz1.id, 'question': 'In Git, what is a "commit"?', 'question_type': 'multiple_choice', 'options': json.dumps(['A saved snapshot of changes', 'A request to merge code', 'A type of error', 'A backup copy']), 'correct_answer': 'A saved snapshot of changes', 'explanation': 'A commit is a snapshot of your changes with a descriptive message.'},
        {'quiz_id': quiz1.id, 'question': 'Fill in the blank: "We need to ____ the new feature to production."', 'question_type': 'fill_blank', 'options': json.dumps([]), 'correct_answer': 'deploy', 'explanation': '"Deploy" means to release code to production.'},
        {'quiz_id': quiz1.id, 'question': 'Which word means "finding and fixing errors"?', 'question_type': 'multiple_choice', 'options': json.dumps(['Debugging', 'Deploying', 'Refactoring', 'Caching']), 'correct_answer': 'Debugging', 'explanation': 'Debugging is identifying and removing errors from code.'},
        {'quiz_id': quiz1.id, 'question': 'Correct: "I have push the code yesterday."', 'question_type': 'sentence_correction', 'options': json.dumps([]), 'correct_answer': 'I pushed the code yesterday.', 'explanation': 'Use past simple with specific past time like "yesterday".'},
    ]

    for q in questions_data:
        db.session.add(QuizQuestion(**q))

    speaking_data = [
        {'title': 'Introducing Yourself', 'scenario': 'It is your first day as an intern. Introduce yourself to the team.', 'category': 'introduction', 'difficulty': 'beginner', 'sample_response': 'Hi everyone! My name is [Name], and I am excited to join the team as a software development intern.', 'tips': 'Keep it concise, mention skills, show enthusiasm.'},
        {'title': 'Explaining a Technical Problem', 'scenario': 'Explain to your senior why the login feature is not working.', 'category': 'technical', 'difficulty': 'intermediate', 'sample_response': 'After investigating, I found the login issue occurs when users have special characters in their passwords.', 'tips': 'Explain the problem, cause, and your plan.'},
        {'title': 'Asking for Help', 'scenario': 'You are stuck on a bug. Ask a teammate for help.', 'category': 'communication', 'difficulty': 'beginner', 'sample_response': 'Hey [Name], do you have a few minutes? I have been working on this bug and could use a fresh perspective.', 'tips': 'Explain what you tried and be specific.'},
        {'title': 'Responding to Critical Feedback', 'scenario': 'Your code review has concerns. How do you respond?', 'category': 'professional', 'difficulty': 'intermediate', 'sample_response': 'Thank you for the detailed feedback. I will refactor those sections and add the validation checks you suggested.', 'tips': 'Thank them, acknowledge points, explain your plan.'},
    ]

    for scenario in speaking_data:
        db.session.add(SpeakingScenario(**scenario))

    interview_data = [
        {'question': 'Tell me about yourself.', 'category': 'general', 'difficulty': 'beginner', 'sample_answer': 'I am a CS student with experience in React and Node.js.', 'tips': 'Focus on relevant experience and why you want this role.'},
        {'question': 'What is your greatest weakness?', 'category': 'behavioral', 'difficulty': 'intermediate', 'sample_answer': 'I sometimes spend too long solving problems alone before asking for help.', 'tips': 'Choose a real weakness and show improvement.'},
        {'question': 'Describe a challenging bug you fixed.', 'category': 'technical', 'difficulty': 'intermediate', 'sample_answer': 'A random logout bug took three days to solve - it was a timezone mismatch.', 'tips': 'Use STAR method: Situation, Task, Action, Result.'},
        {'question': 'Why do you want to work here?', 'category': 'motivation', 'difficulty': 'beginner', 'sample_answer': 'I am impressed by your focus on developer tools and open source contributions.', 'tips': 'Research the company and connect your goals.'},
    ]

    for q in interview_data:
        db.session.add(InterviewQuestion(**q))

    reading_data = [
        {'title': 'Understanding REST APIs', 'category': 'technical', 'difficulty': 'beginner', 'word_count': 300, 'reading_time_minutes': 2, 'content': 'REST (Representational State Transfer) is an architectural style for designing APIs. REST APIs use HTTP methods like GET, POST, PUT, and DELETE to perform operations on resources. Key principles: Stateless, Client-Server, Cacheable, Uniform Interface.'},
        {'title': 'Version Control with Git', 'category': 'technical', 'difficulty': 'intermediate', 'word_count': 350, 'reading_time_minutes': 3, 'content': 'Git is the most widely used version control system. Key concepts: Repository, Commit, Branch, Merge, Clone. Common workflow: clone, create branch, make changes, commit, push, create pull request.'},
        {'title': 'Agile Development', 'category': 'methodology', 'difficulty': 'beginner', 'word_count': 280, 'reading_time_minutes': 2, 'content': 'Agile emphasizes flexibility and collaboration. Key concepts: Sprint, Standup, Retrospective, Backlog, User Story. Values: Individuals over processes, Working software over documentation, Customer collaboration, Responding to change.'},
    ]

    for article in reading_data:
        db.session.add(ReadingArticle(**article))

    db.session.commit()
    print('Database seeded successfully.')


# ==================== API ROUTES ====================

# Serve frontend
@app.route('/')
def serve_index():
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('../frontend', path)


# Authentication Routes
@app.route('/api/auth/signup', methods=['POST'])
def signup():
    """Register a new user."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    full_name = data.get('full_name', '').strip()

    if not username or not email or not password:
        return jsonify({'error': 'Username, email, and password are required'}), 400

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    if '@' not in email:
        return jsonify({'error': 'Invalid email format'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    user = User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        full_name=full_name
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': user.to_dict()
    }), 201


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return token."""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    user = User.query.filter(
        (User.username == username) | (User.email == username)
    ).first()

    if not user or not verify_password(password, user.password_hash):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user.id)
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    })


@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_current_user(user_id):
    """Get current authenticated user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()})


# Dashboard Routes
@app.route('/api/dashboard', methods=['GET'])
@token_required
def get_dashboard(user_id):
    """Get dashboard data for the user."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    total_lessons = Lesson.query.count()
    completed_lessons = UserProgress.query.filter_by(
        user_id=user_id, completed=True
    ).count()

    total_quizzes = Quiz.query.count()
    quiz_attempts = QuizAttempt.query.filter_by(user_id=user_id).count()
    avg_score = db.session.query(db.func.avg(QuizAttempt.score)).filter_by(
        user_id=user_id
    ).scalar() or 0

    total_vocab = Vocabulary.query.count()
    words_learned = UserVocabulary.query.filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.mastery_level >= 3
    ).count()

    today = date.today()
    today_activity = DailyActivity.query.filter_by(
        user_id=user_id, activity_date=today
    ).first()

    recent_chat = ChatHistory.query.filter_by(user_id=user_id).order_by(
        ChatHistory.created_at.desc()
    ).limit(5).all()

    return jsonify({
        'user': user.to_dict(),
        'stats': {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'lesson_progress': round((completed_lessons / total_lessons * 100) if total_lessons > 0 else 0, 1),
            'total_quizzes': total_quizzes,
            'quizzes_taken': quiz_attempts,
            'average_score': round(avg_score, 1),
            'total_vocabulary': total_vocab,
            'words_learned': words_learned,
            'streak_days': user.streak_days,
            'daily_goal_minutes': user.daily_goal_minutes,
            'today_minutes': today_activity.minutes_active if today_activity else 0,
        },
        'recent_activity': [chat.to_dict() for chat in recent_chat]
    })


# Lessons Routes
@app.route('/api/lessons', methods=['GET'])
@token_required
def get_lessons(user_id):
    """Get all lessons with user progress."""
    category = request.args.get('category')
    query = Lesson.query

    if category:
        query = query.filter_by(category=category)

    lessons = query.order_by(Lesson.order_index).all()
    progress = UserProgress.query.filter_by(user_id=user_id).all()
    progress_map = {p.lesson_id: p for p in progress}

    result = []
    for lesson in lessons:
        lesson_dict = lesson.to_dict()
        lesson_dict['user_progress'] = progress_map.get(lesson.id).to_dict() if lesson.id in progress_map else None
        result.append(lesson_dict)

    return jsonify({'lessons': result})


@app.route('/api/lessons/<int:lesson_id>', methods=['GET'])
@token_required
def get_lesson(user_id, lesson_id):
    """Get a specific lesson."""
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    progress = UserProgress.query.filter_by(
        user_id=user_id, lesson_id=lesson_id
    ).first()

    lesson_dict = lesson.to_dict()
    lesson_dict['user_progress'] = progress.to_dict() if progress else None
    return jsonify({'lesson': lesson_dict})


@app.route('/api/lessons/<int:lesson_id>/complete', methods=['POST'])
@token_required
def complete_lesson(user_id, lesson_id):
    """Mark a lesson as completed."""
    lesson = Lesson.query.get(lesson_id)
    if not lesson:
        return jsonify({'error': 'Lesson not found'}), 404

    progress = UserProgress.query.filter_by(
        user_id=user_id, lesson_id=lesson_id
    ).first()

    if not progress:
        progress = UserProgress(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=True,
            completed_at=datetime.utcnow()
        )
        db.session.add(progress)
    else:
        progress.completed = True
        progress.completed_at = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Lesson marked as complete', 'progress': progress.to_dict()})


# Vocabulary Routes
@app.route('/api/vocabulary', methods=['GET'])
@token_required
def get_vocabulary(user_id):
    """Get vocabulary list with user mastery."""
    category = request.args.get('category')
    query = Vocabulary.query

    if category:
        query = query.filter_by(category=category)

    vocab_list = query.all()
    user_vocab = UserVocabulary.query.filter_by(user_id=user_id).all()
    mastery_map = {uv.vocab_id: uv for uv in user_vocab}

    result = []
    for vocab in vocab_list:
        vocab_dict = vocab.to_dict()
        vocab_dict['mastery'] = mastery_map.get(vocab.id).to_dict() if vocab.id in mastery_map else None
        result.append(vocab_dict)

    return jsonify({'vocabulary': result})


@app.route('/api/vocabulary/<int:vocab_id>/review', methods=['POST'])
@token_required
def review_vocabulary(user_id, vocab_id):
    """Record vocabulary review."""
    vocab = Vocabulary.query.get(vocab_id)
    if not vocab:
        return jsonify({'error': 'Vocabulary not found'}), 404

    data = request.get_json() or {}
    correct = data.get('correct', True)

    user_vocab = UserVocabulary.query.filter_by(
        user_id=user_id, vocab_id=vocab_id
    ).first()

    if not user_vocab:
        user_vocab = UserVocabulary(
            user_id=user_id,
            vocab_id=vocab_id,
            mastery_level=1 if correct else 0,
            times_reviewed=1,
            last_reviewed=datetime.utcnow()
        )
        db.session.add(user_vocab)
    else:
        user_vocab.times_reviewed += 1
        if correct and user_vocab.mastery_level < 5:
            user_vocab.mastery_level += 1
        elif not correct and user_vocab.mastery_level > 0:
            user_vocab.mastery_level -= 1
        user_vocab.last_reviewed = datetime.utcnow()

    db.session.commit()
    return jsonify({'message': 'Review recorded', 'mastery': user_vocab.to_dict()})


# Quiz Routes
@app.route('/api/quizzes', methods=['GET'])
@token_required
def get_quizzes(user_id):
    """Get all available quizzes."""
    quizzes = Quiz.query.all()
    return jsonify({'quizzes': [q.to_dict() for q in quizzes]})


@app.route('/api/quizzes/<int:quiz_id>', methods=['GET'])
@token_required
def get_quiz(user_id, quiz_id):
    """Get quiz with questions (without answers)."""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()
    quiz_dict = quiz.to_dict()
    quiz_dict['questions'] = [q.to_dict() for q in questions]
    return jsonify({'quiz': quiz_dict})


@app.route('/api/quizzes/<int:quiz_id>/submit', methods=['POST'])
@token_required
def submit_quiz(user_id, quiz_id):
    """Submit quiz answers and get score."""
    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return jsonify({'error': 'Quiz not found'}), 404

    data = request.get_json()
    if not data or 'answers' not in data:
        return jsonify({'error': 'Answers are required'}), 400

    answers = data['answers']
    # Handle case where answers might be a JSON string
    if isinstance(answers, str):
        try:
            answers = json.loads(answers)
        except (json.JSONDecodeError, TypeError):
            return jsonify({'error': 'Invalid answers format'}), 400

    if not isinstance(answers, dict):
        return jsonify({'error': 'Answers must be a dictionary'}), 400

    questions = QuizQuestion.query.filter_by(quiz_id=quiz_id).all()

    if not questions:
        return jsonify({'error': 'No questions found for this quiz'}), 400

    correct_count = 0
    total_points = 0
    earned_points = 0
    results = []

    for question in questions:
        total_points += question.points
        user_answer = answers.get(str(question.id), '')
        is_correct = user_answer.lower().strip() == question.correct_answer.lower().strip()

        if is_correct:
            correct_count += 1
            earned_points += question.points

        results.append({
            'question_id': question.id,
            'user_answer': user_answer,
            'correct_answer': question.correct_answer,
            'is_correct': is_correct,
            'explanation': question.explanation
        })

    score = (earned_points / total_points * 100) if total_points > 0 else 0

    attempt = QuizAttempt(
        user_id=user_id,
        quiz_id=quiz_id,
        score=score,
        total_questions=len(questions),
        answers=json.dumps(answers)
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({
        'message': 'Quiz submitted',
        'score': round(score, 1),
        'correct': correct_count,
        'total': len(questions),
        'results': results
    })


@app.route('/api/quizzes/history', methods=['GET'])
@token_required
def get_quiz_history(user_id):
    """Get user's quiz history."""
    attempts = QuizAttempt.query.filter_by(user_id=user_id).order_by(
        QuizAttempt.completed_at.desc()
    ).all()
    return jsonify({'attempts': [a.to_dict() for a in attempts]})


# AI Tutor Routes
@app.route('/api/tutor/chat', methods=['POST'])
@token_required
def chat_with_tutor(user_id):
    """Send message to AI tutor and get correction."""
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'Message is required'}), 400

    message = data['message'].strip()
    if not message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    analysis = EnglishTutor.analyze_message(message)
    response = EnglishTutor.generate_response(analysis)

    chat = ChatHistory(
        user_id=user_id,
        user_message=message,
        tutor_response=response,
        corrections=json.dumps(analysis['corrections'])
    )
    db.session.add(chat)
    db.session.commit()

    return jsonify({
        'response': response,
        'analysis': analysis,
        'chat_id': chat.id
    })


@app.route('/api/tutor/history', methods=['GET'])
@token_required
def get_chat_history(user_id):
    """Get user's chat history."""
    chats = ChatHistory.query.filter_by(user_id=user_id).order_by(
        ChatHistory.created_at.desc()
    ).limit(50).all()
    return jsonify({'history': [c.to_dict() for c in chats]})


# Practice Routes
@app.route('/api/practice/speaking', methods=['GET'])
@token_required
def get_speaking_scenarios(user_id):
    """Get speaking practice scenarios."""
    scenarios = SpeakingScenario.query.all()
    return jsonify({'scenarios': [s.to_dict() for s in scenarios]})


@app.route('/api/practice/writing/prompts', methods=['GET'])
@token_required
def get_writing_prompts(user_id):
    """Get writing practice prompts."""
    prompts = [
        {
            'id': 1,
            'type': 'email',
            'prompt': 'Write an email to your team lead requesting an extension on a project deadline. Explain why you need more time and propose a new timeline.'
        },
        {
            'id': 2,
            'type': 'slack',
            'prompt': 'Write a Slack message to your team explaining that you found a bug in the authentication module and are working on a fix.'
        },
        {
            'id': 3,
            'type': 'standup',
            'prompt': 'Write your daily standup update. Mention what you completed yesterday, what you are working on today, and any blockers.'
        },
        {
            'id': 4,
            'type': 'bug_report',
            'prompt': 'Write a bug report for an issue where the login button does not respond when clicked on mobile devices.'
        },
        {
            'id': 5,
            'type': 'pr_description',
            'prompt': 'Write a pull request description for a new feature that adds dark mode support to the application.'
        },
        {
            'id': 6,
            'type': 'documentation',
            'prompt': 'Write documentation for a new API endpoint that allows users to reset their password via email.'
        },
    ]
    return jsonify({'prompts': prompts})


@app.route('/api/practice/writing/submit', methods=['POST'])
@token_required
def submit_writing(user_id):
    """Submit writing for feedback."""
    data = request.get_json()
    if not data or 'submission' not in data or 'prompt' not in data:
        return jsonify({'error': 'Submission and prompt are required'}), 400

    submission = WritingSubmission(
        user_id=user_id,
        prompt=data['prompt'],
        submission=data['submission'],
        submission_type=data.get('type', 'general')
    )
    db.session.add(submission)
    db.session.commit()

    return jsonify({
        'message': 'Submission received',
        'submission': submission.to_dict()
    })


# Interview Routes
@app.route('/api/interview/questions', methods=['GET'])
@token_required
def get_interview_questions(user_id):
    """Get interview questions."""
    category = request.args.get('category')
    query = InterviewQuestion.query

    if category:
        query = query.filter_by(category=category)

    questions = query.all()
    return jsonify({'questions': [q.to_dict() for q in questions]})


# Reading Routes
@app.route('/api/reading/articles', methods=['GET'])
@token_required
def get_reading_articles(user_id):
    """Get reading practice articles."""
    articles = ReadingArticle.query.all()
    return jsonify({'articles': [a.to_dict() for a in articles]})


# Progress Routes
@app.route('/api/progress', methods=['GET'])
@token_required
def get_progress(user_id):
    """Get detailed progress data."""
    lessons_completed = UserProgress.query.filter_by(
        user_id=user_id, completed=True
    ).count()

    total_lessons = Lesson.query.count()

    quiz_stats = db.session.query(
        db.func.count(QuizAttempt.id),
        db.func.avg(QuizAttempt.score),
        db.func.max(QuizAttempt.score)
    ).filter_by(user_id=user_id).first()

    vocab_mastered = UserVocabulary.query.filter(
        UserVocabulary.user_id == user_id,
        UserVocabulary.mastery_level >= 3
    ).count()

    total_vocab = Vocabulary.query.count()

    recent_quizzes = QuizAttempt.query.filter_by(user_id=user_id).order_by(
        QuizAttempt.completed_at.desc()
    ).limit(10).all()

    return jsonify({
        'lessons': {
            'completed': lessons_completed,
            'total': total_lessons,
            'percentage': round((lessons_completed / total_lessons * 100) if total_lessons > 0 else 0, 1)
        },
        'quizzes': {
            'attempts': quiz_stats[0] or 0,
            'average_score': round(quiz_stats[1] or 0, 1),
            'best_score': round(quiz_stats[2] or 0, 1)
        },
        'vocabulary': {
            'mastered': vocab_mastered,
            'total': total_vocab,
            'percentage': round((vocab_mastered / total_vocab * 100) if total_vocab > 0 else 0, 1)
        },
        'recent_quizzes': [q.to_dict() for q in recent_quizzes]
    })


# Settings Routes
@app.route('/api/settings', methods=['GET'])
@token_required
def get_settings(user_id):
    """Get user settings."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'settings': {
            'daily_goal_minutes': user.daily_goal_minutes,
            'full_name': user.full_name,
            'email': user.email
        }
    })


@app.route('/api/settings', methods=['PUT'])
@token_required
def update_settings(user_id):
    """Update user settings."""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400

    if 'daily_goal_minutes' in data:
        user.daily_goal_minutes = max(5, min(120, int(data['daily_goal_minutes'])))

    if 'full_name' in data:
        user.full_name = data['full_name'].strip()

    db.session.commit()
    return jsonify({'message': 'Settings updated', 'user': user.to_dict()})


# ==================== MAIN ====================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()

    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', '1') == '1'
    print(f"Starting English Tutor on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=debug)
