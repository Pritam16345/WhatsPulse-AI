# WhatsPulse AI — WhatsApp Insights

A production-grade analytics tool for WhatsApp chat exports. Built with Flask (Python), React (JS), and Google Gemini AI.

## 📁 Project Structure
```
whatsapp_analyzer/
├── backend/            # Python Flask Backend
│   ├── app.py          # API Routes & Web Server
│   ├── parser.py       # Chat Parsing Engine
│   ├── analyzer.py     # Statistical Analysis
│   ├── ai_features.py  # Gemini AI Integration
│   └── requirements.txt
├── frontend/           # React Frontend (Vite)
│   ├── src/            # Components & Logic
│   └── dist/           # Production Build
├── .env                # Environment Variables (API Keys)
└── .gitignore          # Git exclusion rules
```

## 🚀 Quick Start (Production Mode)

1. **Setup Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure API Key**:
   Create a `.env` file in the root directory (or use the provided template) and add your Gemini API key:
   ```env
   GEMINI_API_KEY=your_key_here
   ```

3. **Run Application**:
   ```bash
   python backend/app.py
   ```
   Open **`http://localhost:5000`** in your browser.

## 🛠️ Development Mode

### Backend
```bash
cd backend
python app.py
```
(Runs on port 5000)

### Frontend
```bash
cd frontend
npm install
npm run dev
```
(Runs on port 3000 with proxy to 5000)

## 📊 Features
- **Comprehensive Stats**: Messages, words, media, links, deleted, and edited counts.
- **Activity Analysis**: Timelines, heatmaps, and peak velocity tracking.
- **User Dynamics**: Response times, conversation starters, and ghosting detection.
- **Linguistic Analysis**: Word frequency, emoji stats, and language distribution.
- **AI-Powered**: Summaries, RAG-based Q&A, and personality profiles using Google Gemini.
- **Visualizations**: Interactive charts (Chart.js) and network graphs (vis.js).
