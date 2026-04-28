# WhatsApp Chat Analyzer

A powerful personal/professional tool that extracts every possible insight from your WhatsApp chat exports. Built with Flask, React, and Claude AI.

## Features
- **Deep Analytics**: Timelines, heatmaps, word frequencies, and emoji stats.
- **User Insights**: Response times, conversation starters, and ghost analysis.
- **Content Analysis**: Links sharing, media patterns, and deleted messages.
- **AI-Powered**: Summaries, Q&A about your chat, and fun personality profiles.
- **Interactive**: Dynamic charts and conversation network graphs.

## Setup

### 1. Prerequisites
- Python 3.8+
- Node.js (for frontend development)

### 2. Backend Setup
```bash
pip install -r requirements.txt
```

### 3. Frontend Setup (Development)
```bash
cd frontend
npm install
npm run dev
```

### 4. AI Features (Optional)
To enable AI features, set your Anthropic API key:
```bash
# Windows
set ANTHROPIC_API_KEY=your_key_here
# Linux/Mac
export ANTHROPIC_API_KEY=your_key_here
```

## Running the App

### Development Mode
1. Start Flask: `python app.py` (runs on port 5000)
2. Start Vite: `cd frontend && npm run dev` (runs on port 3000)
3. Open `http://localhost:3000`

### Production Mode
1. Build frontend: `cd frontend && npm run build`
2. Run Flask: `python app.py`
3. Open `http://localhost:5000`

## Exporting Your Chat
1. Open WhatsApp on your phone.
2. Go to the chat you want to analyze.
3. Tap the three dots (⋮) → **More** → **Export Chat**.
4. Select **Without Media**.
5. Save the `.txt` file and upload it to the analyzer!
