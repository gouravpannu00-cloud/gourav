import os
from flask import Flask, render_template, request, jsonify
import sqlite3
import datetime
import speech_recognition as sr
import pyttsx3
import base64
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'voice-assistant-secret-key')
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'voice_assistant.db')

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            response TEXT NOT NULL,
            command_type TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/process', methods=['POST'])
def process_command():
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        if not command:
            return jsonify({'error': 'Empty command', 'status': 'error'})
        if len(command) > 500:
            return jsonify({'error': 'Command too long. Please keep it under 500 characters.', 'status': 'error'})
        result = handle_command(command)
        save_command(command, result['text'], result.get('type', 'general'))
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': 'Something went wrong processing your command. Please try again.', 'status': 'error'})

@app.route('/api/tts', methods=['POST'])
def text_to_speech():
    data = request.get_json()
    text = data.get('text', '').strip()
    if not text:
        return jsonify({'error': 'Empty text'}), 400
    if len(text) > 1000:
        text = text[:1000] + '...'
    temp_path = os.path.join(os.path.dirname(DATABASE), 'temp_audio.mp3')
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 160)
        engine.setProperty('volume', 0.9)
        engine.save_to_file(text, temp_path)
        engine.runAndWait()
        if not os.path.exists(temp_path):
            return jsonify({'error': 'Audio generation failed'}), 500
        with open(temp_path, 'rb') as f:
            audio_data = f.read()
        os.remove(temp_path)
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        return jsonify({'audio': audio_base64})
    except Exception as e:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except:
            pass
        return jsonify({'audio': None, 'error': str(e)}), 500

@app.route('/api/notes', methods=['GET'])
def get_notes():
    conn = get_db_connection()
    notes = conn.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
    conn.close()
    return jsonify([dict(note) for note in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    note = data.get('note', '').strip()
    if not note:
        return jsonify({'error': 'Note cannot be empty'}), 400
    conn = get_db_connection()
    conn.execute('INSERT INTO notes (note) VALUES (?)', (note,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Note saved successfully'})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Note deleted'})

@app.route('/api/history', methods=['GET'])
def get_history():
    conn = get_db_connection()
    history = conn.execute('SELECT * FROM command_history ORDER BY timestamp DESC LIMIT 50').fetchall()
    conn.close()
    return jsonify([dict(item) for item in history])

@app.route('/api/history', methods=['DELETE'])
def clear_history():
    conn = get_db_connection()
    conn.execute('DELETE FROM command_history')
    conn.commit()
    conn.close()
    return jsonify({'message': 'History cleared'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    conn = get_db_connection()
    today = datetime.date.today().isoformat()
    commands_today = conn.execute(
        'SELECT COUNT(*) as count FROM command_history WHERE date(timestamp) = ?',
        (today,)
    ).fetchone()['count']
    notes_count = conn.execute('SELECT COUNT(*) as count FROM notes').fetchone()['count']
    total_commands = conn.execute('SELECT COUNT(*) as count FROM command_history').fetchone()['count']
    conn.close()
    return jsonify({
        'commands_today': commands_today,
        'notes_count': notes_count,
        'total_commands': total_commands
    })

def save_command(command, response, command_type):
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO command_history (command, response, command_type) VALUES (?, ?, ?)',
        (command, response, command_type)
    )
    conn.commit()
    conn.close()

def handle_command(command):
    cmd = command.lower().strip()

    if re.search(r'\b(hello|hi|hey|good morning|good afternoon|good evening)\b', cmd):
        hour = datetime.datetime.now().hour
        if hour < 12:
            greeting = 'Good morning! How can I help you today?'
        elif hour < 18:
            greeting = 'Good afternoon! How can I help you?'
        else:
            greeting = 'Good evening! How can I assist you?'
        return {'text': greeting, 'type': 'greeting', 'status': 'ready'}

    if re.search(r'\b(time|clock|hour)\b', cmd):
        now = datetime.datetime.now()
        time_str = now.strftime('%I:%M %p')
        return {'text': f'The current time is {time_str}', 'type': 'time', 'status': 'ready'}

    if re.search(r'\b(date|day|today)\b', cmd):
        today = datetime.date.today().strftime('%A, %B %d, %Y')
        return {'text': f'Today is {today}', 'type': 'date', 'status': 'ready'}

    if re.search(r'\b(joke|funny|laugh)\b', cmd):
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the developer go broke? Because he used up all his cache.",
            "How do you comfort a JavaScript bug? You console it.",
            "Why do Python programmers wear glasses? Because they can't C#.",
            "What's a computer's favorite snack? Microchips!",
            "Why was the computer cold? It left its Windows open.",
            "How many programmers does it take to change a light bulb? None, that's a hardware problem."
        ]
        return {'text': jokes[int(datetime.datetime.now().timestamp()) % len(jokes)], 'type': 'joke', 'status': 'ready'}

    if 'calculate' in cmd or re.search(r'\bwhat is\b', cmd) and any(op in cmd for op in ['+', '-', 'times', 'divided', 'multiply', 'x', '*']):
        math_expr = cmd
        math_expr = math_expr.replace('divided by', '/').replace('multiplied by', '*').replace('times', '*').replace('plus', '+').replace('minus', '-')
        math_expr = re.sub(r'[^0-9+\-*/().]', '', math_expr)
        math_expr = math_expr.replace('x', '*')
        if math_expr:
            try:
                result = eval(math_expr)
                return {'text': f'The result is {result}', 'type': 'calculator', 'status': 'ready'}
            except:
                return {'text': 'Sorry, I could not calculate that. Please try again.', 'type': 'calculator', 'status': 'error'}
        return {'text': 'What would you like me to calculate?', 'type': 'calculator', 'status': 'ready'}

    if re.search(r'\b(open|launch|go to|visit)\b', cmd):
        url_match = re.search(r'(?:open|launch|go to|visit)\s+(?:www\.)?([a-zA-Z0-9-]+\.[a-z]{2,})', cmd)
        if url_match:
            domain = url_match.group(1)
            url = f'https://{domain}'
            return {
                'text': f'Opening {domain}',
                'type': 'open_website',
                'action': {'type': 'open_url', 'url': url},
                'status': 'ready'
            }
        return {'text': 'Which website would you like me to open?', 'type': 'open_website', 'status': 'ready'}

    if re.search(r'\b(search|google|look up|find)\b', cmd):
        query = re.sub(r'(search|google|look up|find|for|web)\s*', '', cmd).strip()
        if query:
            search_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
            return {
                'text': f'Searching for {query}',
                'type': 'search',
                'action': {'type': 'open_url', 'url': search_url},
                'status': 'ready'
            }
        return {'text': 'What would you like me to search for?', 'type': 'search', 'status': 'ready'}

    if re.search(r'\b(save note|take note|note that|remember this|write this)\b', cmd):
        note_text = re.sub(r'(save note|take note|note that|remember this|write this)[:\s]+', '', cmd).strip()
        if note_text:
            conn = get_db_connection()
            conn.execute('INSERT INTO notes (note) VALUES (?)', (note_text,))
            conn.commit()
            conn.close()
            return {'text': f'Note saved: {note_text}', 'type': 'note', 'status': 'ready'}
        return {'text': 'What would you like me to note down?', 'type': 'note', 'status': 'ready'}

    if re.search(r'\b(show notes|my notes|list notes|view notes|read notes)\b', cmd):
        conn = get_db_connection()
        notes = conn.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
        conn.close()
        if notes:
            notes_list = '. '.join([f'{n["note"]}' for n in notes[:5]])
            return {'text': f'Your notes: {notes_list}', 'type': 'notes_list', 'status': 'ready'}
        return {'text': 'You have no saved notes yet.', 'type': 'notes_list', 'status': 'ready'}

    if re.search(r'\b(delete note|remove note)\b', cmd):
        conn = get_db_connection()
        notes = conn.execute('SELECT * FROM notes ORDER BY created_at DESC').fetchall()
        conn.close()
        if notes:
            return {
                'text': f'Deleted your most recent note: {notes[0]["note"]}',
                'type': 'delete_note',
                'action': {'type': 'delete_note', 'id': notes[0]['id']},
                'status': 'ready'
            }
        return {'text': 'You have no notes to delete.', 'type': 'delete_note', 'status': 'ready'}

    if re.search(r'\b(history|command history|what did i say|past commands)\b', cmd):
        conn = get_db_connection()
        history = conn.execute('SELECT * FROM command_history ORDER BY timestamp DESC LIMIT 5').fetchall()
        conn.close()
        if history:
            hist_list = '. '.join([f'{h["command"]}' for h in history])
            return {'text': f'Recent commands: {hist_list}', 'type': 'history', 'status': 'ready'}
        return {'text': 'No command history yet.', 'type': 'history', 'status': 'ready'}

    if re.search(r'\b(clear history|delete history|remove history)\b', cmd):
        conn = get_db_connection()
        conn.execute('DELETE FROM command_history')
        conn.commit()
        conn.close()
        return {'text': 'Command history cleared.', 'type': 'clear_history', 'status': 'ready'}

    if re.search(r'\b(who are you|what are you|your name)\b', cmd):
        return {'text': 'I am your Voice Assistant. I can help you with time, date, calculations, notes, web search, and more!', 'type': 'info', 'status': 'ready'}

    if re.search(r'\b(help|what can you do|commands|capabilities)\b', cmd):
        return {
            'text': 'I can help with: time, date, calculations, web search, opening websites, saving notes, telling jokes, and showing command history. Just ask!',
            'type': 'help',
            'status': 'ready'
        }

    if re.search(r'\b(thank|thanks)\b', cmd):
        return {'text': 'You are welcome! Is there anything else I can help with?', 'type': 'greeting', 'status': 'ready'}

    if re.search(r'\b(bye|goodbye|see you|exit)\b', cmd):
        return {'text': 'Goodbye! Have a great day!', 'type': 'greeting', 'status': 'ready'}

    if re.search(r'\b(status|how are you)\b', cmd):
        return {'text': 'I am online and ready to help! All systems are functioning normally.', 'type': 'info', 'status': 'ready'}

    return {'text': f'I did not understand "{command}". Try asking for time, date, a joke, or say "help" to see what I can do.', 'type': 'unknown', 'status': 'error'}

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
