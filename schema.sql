"""
English Tutor - Database Schema
Run this file to initialize the database manually.
The application also auto-creates tables on first run.
"""

-- Users table for authentication and profile
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    daily_goal_minutes INTEGER DEFAULT 30,
    streak_days INTEGER DEFAULT 0,
    last_active_date DATE
);

-- Lessons table for structured learning content
CREATE TABLE IF NOT EXISTS lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'beginner',
    order_index INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User progress tracking for lessons
CREATE TABLE IF NOT EXISTS user_progress (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    lesson_id INTEGER NOT NULL,
    completed BOOLEAN DEFAULT 0,
    completed_at DATETIME,
    score FLOAT DEFAULT 0,
    time_spent_minutes INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);

-- Technical vocabulary database
CREATE TABLE IF NOT EXISTS vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word VARCHAR(100) NOT NULL,
    definition TEXT NOT NULL,
    example TEXT,
    category VARCHAR(50),
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- User vocabulary mastery tracking
CREATE TABLE IF NOT EXISTS user_vocabulary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    vocab_id INTEGER NOT NULL,
    mastery_level INTEGER DEFAULT 0,
    times_reviewed INTEGER DEFAULT 0,
    last_reviewed DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (vocab_id) REFERENCES vocabulary(id)
);

-- Quizzes table
CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Quiz questions with various types
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    question_type VARCHAR(30) NOT NULL,
    options TEXT,
    correct_answer TEXT NOT NULL,
    explanation TEXT,
    points INTEGER DEFAULT 1,
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

-- Quiz attempt records
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    quiz_id INTEGER NOT NULL,
    score FLOAT NOT NULL,
    total_questions INTEGER NOT NULL,
    completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    answers TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
);

-- AI tutor chat history
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    user_message TEXT NOT NULL,
    tutor_response TEXT NOT NULL,
    corrections TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Daily activity log for streak tracking
CREATE TABLE IF NOT EXISTS daily_activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    activity_date DATE NOT NULL,
    minutes_active INTEGER DEFAULT 0,
    lessons_completed INTEGER DEFAULT 0,
    quizzes_completed INTEGER DEFAULT 0,
    words_learned INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE(user_id, activity_date)
);

-- Writing practice submissions
CREATE TABLE IF NOT EXISTS writing_submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    submission TEXT NOT NULL,
    feedback TEXT,
    score FLOAT,
    submission_type VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Speaking practice scenarios
CREATE TABLE IF NOT EXISTS speaking_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    scenario TEXT NOT NULL,
    category VARCHAR(50),
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    sample_response TEXT,
    tips TEXT
);

-- Interview questions for developer roles
CREATE TABLE IF NOT EXISTS interview_questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question TEXT NOT NULL,
    category VARCHAR(50),
    difficulty VARCHAR(20),
    sample_answer TEXT,
    tips TEXT
);

-- Reading practice articles
CREATE TABLE IF NOT EXISTS reading_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50),
    difficulty VARCHAR(20),
    word_count INTEGER,
    reading_time_minutes INTEGER
);
