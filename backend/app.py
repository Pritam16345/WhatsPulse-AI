"""
WhatsApp Chat Analyzer — Flask backend with all routes and logic.
"""

import os
import uuid
import json
import time
import zipfile
import io
import threading
from flask import Flask, render_template, request, jsonify, abort, send_file, send_from_directory
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

from parser import parse_chat, get_users
from analyzer import (
    get_overview_stats, get_user_stats, get_timeline_data, get_activity_heatmap,
    get_word_frequency, get_emoji_stats, get_response_time_stats,
    get_conversation_starters, get_url_analysis, get_sentiment_over_time,
    get_deleted_message_analysis, get_media_analysis, get_longest_messages,
    get_ghost_analysis, get_poll_analysis, get_night_owl_stats,
    get_conversation_network, get_late_replies, get_language_stats,
)
from ai_features import summarize_conversation, answer_question, get_personality_profiles

app = Flask(__name__, static_folder='../frontend/dist', static_url_path='/')
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store parsed DataFrames in memory (session-keyed)
CHAT_STORE = {}  # {session_id: {'df': DataFrame, 'last_access': timestamp}}
CLEANUP_INTERVAL = 1800  # 30 minutes


def _cleanup_old_sessions():
    """Remove sessions older than 30 minutes."""
    now = time.time()
    expired = [sid for sid, data in CHAT_STORE.items()
               if now - data.get('last_access', 0) > CLEANUP_INTERVAL]
    for sid in expired:
        del CHAT_STORE[sid]


def _schedule_cleanup():
    _cleanup_old_sessions()
    timer = threading.Timer(300, _schedule_cleanup)
    timer.daemon = True
    timer.start()


def get_df():
    """Get current session's DataFrame from CHAT_STORE."""
    session_id = request.args.get('session_id')
    if not session_id:
        try:
            body = request.get_json(silent=True)
            if body:
                session_id = body.get('session_id')
        except Exception:
            pass

    if not session_id or session_id not in CHAT_STORE:
        abort(400, description='No chat data found. Please upload a chat file first.')

    CHAT_STORE[session_id]['last_access'] = time.time()
    return CHAT_STORE[session_id]['df']


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')


@app.route('/api/upload', methods=['POST'])
def upload():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if not file.filename:
            return jsonify({'error': 'No file selected'}), 400

        filename = file.filename.lower()

        if filename.endswith('.zip'):
            zip_data = io.BytesIO(file.read())
            with zipfile.ZipFile(zip_data, 'r') as z:
                txt_files = [f for f in z.namelist() if f.endswith('.txt')]
                if not txt_files:
                    return jsonify({'error': 'No .txt file found in ZIP'}), 400
                content = z.read(txt_files[0]).decode('utf-8', errors='ignore')
        elif filename.endswith('.txt'):
            content = file.read().decode('utf-8', errors='ignore')
        else:
            return jsonify({'error': 'Please upload a .txt or .zip file'}), 400

        df = parse_chat(content)
        session_id = str(uuid.uuid4())
        CHAT_STORE[session_id] = {'df': df, 'last_access': time.time()}

        users = get_users(df)
        user_df = df[df['user'] != 'system']

        _cleanup_old_sessions()

        return jsonify({
            'success': True,
            'session_id': session_id,
            'users': users,
            'total_messages': int(len(user_df)),
            'date_range': f"{user_df['datetime'].min().strftime('%b %d, %Y')} — {user_df['datetime'].max().strftime('%b %d, %Y')}",
            'first_date': str(user_df['datetime'].min().date()),
            'last_date': str(user_df['datetime'].max().date()),
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Failed to parse chat: {str(e)}'}), 500


@app.route('/api/overview')
def overview():
    try:
        return jsonify(get_overview_stats(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users')
def users():
    try:
        return jsonify(get_user_stats(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/timeline')
def timeline():
    try:
        g = request.args.get('granularity', 'daily')
        u = request.args.get('user', None)
        return jsonify(get_timeline_data(get_df(), granularity=g, user=u))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/heatmap')
def heatmap():
    try:
        return jsonify(get_activity_heatmap(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/words')
def words():
    try:
        u = request.args.get('user', None)
        return jsonify(get_word_frequency(get_df(), user=u))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/emojis')
def emojis():
    try:
        u = request.args.get('user', None)
        return jsonify(get_emoji_stats(get_df(), user=u))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/response_time')
def response_time():
    try:
        return jsonify(get_response_time_stats(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/starters')
def starters():
    try:
        return jsonify(get_conversation_starters(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/urls')
def urls():
    try:
        return jsonify(get_url_analysis(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sentiment')
def sentiment():
    try:
        return jsonify(get_sentiment_over_time(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/deleted')
def deleted():
    try:
        return jsonify(get_deleted_message_analysis(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/media')
def media():
    try:
        return jsonify(get_media_analysis(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/network')
def network():
    try:
        return jsonify(get_conversation_network(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/night_owl')
def night_owl():
    try:
        return jsonify(get_night_owl_stats(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/polls')
def polls():
    try:
        return jsonify(get_poll_analysis(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/longest')
def longest():
    try:
        return jsonify(get_longest_messages(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ghost')
def ghost():
    try:
        return jsonify(get_ghost_analysis(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/late_replies')
def late_replies():
    try:
        return jsonify(get_late_replies(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/language')
def language():
    try:
        return jsonify(get_language_stats(get_df()))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/summarize', methods=['POST'])
def ai_summarize():
    try:
        body = request.get_json(silent=True) or {}
        session_id = body.get('session_id')
        if not session_id or session_id not in CHAT_STORE:
            return jsonify({'error': 'No chat data found'}), 400
        CHAT_STORE[session_id]['last_access'] = time.time()
        df = CHAT_STORE[session_id]['df']
        period = body.get('period', 'all')
        user = body.get('user', None)
        result = summarize_conversation(df, period=period, user=user)
        return jsonify({'summary': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/ask', methods=['POST'])
def ai_ask():
    try:
        body = request.get_json(silent=True) or {}
        session_id = body.get('session_id')
        if not session_id or session_id not in CHAT_STORE:
            return jsonify({'error': 'No chat data found'}), 400
        CHAT_STORE[session_id]['last_access'] = time.time()
        df = CHAT_STORE[session_id]['df']
        question = body.get('question', '')
        if not question:
            return jsonify({'error': 'Please provide a question'}), 400
        result = answer_question(df, question)
        return jsonify({'answer': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/ai/personality')
def ai_personality():
    try:
        df = get_df()
        result = get_personality_profiles(df)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/json')
def export_json():
    try:
        df = get_df()
        data = {
            'overview': get_overview_stats(df),
            'users': get_user_stats(df),
            'heatmap': get_activity_heatmap(df),
            'emojis': get_emoji_stats(df),
            'starters': get_conversation_starters(df),
            'urls': get_url_analysis(df),
            'night_owl': get_night_owl_stats(df),
            'polls': get_poll_analysis(df),
        }
        output = io.BytesIO()
        output.write(json.dumps(data, indent=2, default=str).encode('utf-8'))
        output.seek(0)
        return send_file(output, mimetype='application/json',
                         as_attachment=True, download_name='whatsapp_analysis.json')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/csv')
def export_csv():
    try:
        df = get_df()
        export_df = df[df['user'] != 'system'][
            ['datetime', 'user', 'message', 'word_count', 'is_media', 'is_deleted']
        ].copy()
        output = io.BytesIO()
        export_df.to_csv(output, index=False, encoding='utf-8')
        output.seek(0)
        return send_file(output, mimetype='text/csv',
                         as_attachment=True, download_name='whatsapp_messages.csv')
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    _schedule_cleanup()
    # Use PORT from env for Render, default to 5000 for local
    port = int(os.environ.get("PORT", 5000))
    # host='0.0.0.0' is required for external access in deployment
    app.run(host='0.0.0.0', port=port, debug=os.environ.get('FLASK_ENV') == 'development')
