"""
AI Features — Google Gemini integration with graceful degradation.
"""

import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

_API_KEY = os.environ.get('GEMINI_API_KEY', '')
if _API_KEY:
    genai.configure(api_key=_API_KEY)
    _model = genai.GenerativeModel(model_name='gemini-2.5-flash')
else:
    _model = None

_SYSTEM_PROMPT = (
    "You are an expert WhatsApp Chat Analyst. Your goal is to provide "
    "deep, professional, and genuine insights into personal and group conversations. "
    "Always use a structured, analytical tone. Format your output using "
    "professional Markdown (headings, bullet points, bold text). "
    "Do not be generic; mention specific recurring themes, emotional undertones, "
    "and relationship dynamics based on the provided messages.\n\n"
)

def _no_api_message():
    return ("### ⚠️ AI Features Disabled\n\n"
            "AI features require a Google Gemini API key. "
            "Set the `GEMINI_API_KEY` in your `.env` file to enable.")

def summarize_conversation(df, period='all', user=None):
    if not _model:
        return _no_api_message()

    udf = df[df['user'] != 'system'].copy()
    if user and user != 'all':
        udf = udf[udf['user'] == user]

    # Sample messages to stay within token limits while preserving context
    if len(udf) > 500:
        # Take a mix of first, middle, and last messages
        head = udf.head(150)
        tail = udf.tail(150)
        mid = udf.sample(200, random_state=42)
        udf = pd.concat([head, mid, tail]).sort_values('datetime').drop_duplicates(subset=['datetime', 'user', 'message'])
    
    msg_text = '\n'.join(
        f"[{row['datetime'].strftime('%Y-%m-%d %H:%M')}] {row['user']}: {row['message']}"
        for _, row in udf.iterrows()
    )

    prompt = (
        f"Perform a comprehensive psychological and topical analysis of this WhatsApp conversation. "
        f"Provide a 'Genuine Conversation Summary' with the following sections:\n"
        f"1. **Executive Overview**: A 2-sentence summary of the relationship or group nature.\n"
        f"2. **Key Thematic Pillars**: The most significant recurring topics and their emotional weight.\n"
        f"3. **Communication Dynamics**: Analyze the tone, frequency, and power balance.\n"
        f"4. **Notable Milestones**: Significant shifts or events mentioned.\n"
        f"5. **Analytical Insights**: Deep observations about the participants' personalities or goals.\n\n"
        f"Conversation Data:\n{msg_text}"
    )

    try:
        response = _model.generate_content(_SYSTEM_PROMPT + prompt)
        return response.text
    except Exception as e:
        return f"**Error**: Gemini generation failed. ({str(e)})"

def answer_question(df, question):
    if not _model:
        return _no_api_message()

    udf = df[(df['user'] != 'system') & ~df['is_media'] & ~df['is_deleted']]
    
    # Improved context selection
    keywords = [w.lower() for w in question.split() if len(w) > 2]
    scored = []
    for idx, row in udf.iterrows():
        msg = str(row['message']).lower()
        score = sum(2 for kw in keywords if kw in msg) # Exact matches
        score += sum(1 for kw in keywords if any(k in msg for k in [kw[:-1], kw+'s'])) # Partial
        if score > 0:
            scored.append((score, idx))

    scored.sort(key=lambda x: x[0], reverse=True)
    top_indices = [idx for _, idx in scored[:80]]
    relevant = udf.loc[top_indices].sort_values('datetime') if top_indices else udf.tail(60)

    msg_text = '\n'.join(
        f"[{row['datetime'].strftime('%Y-%m-%d %H:%M')}] {row['user']}: {row['message']}"
        for _, row in relevant.iterrows()
    )

    prompt = (
        f"Question: {question}\n\n"
        f"Context (Selected Messages):\n{msg_text}\n\n"
        f"Instructions:\n"
        f"- Answer the question accurately using the context above.\n"
        f"- If the answer isn't in the context, state that clearly.\n"
        f"- Use a professional and direct tone.\n"
        f"- Reference specific dates or users where appropriate."
    )

    try:
        response = _model.generate_content(_SYSTEM_PROMPT + prompt)
        return response.text
    except Exception as e:
        return f"Gemini answer generation failed: {str(e)}"

def get_personality_profiles(df):
    if not _model:
        # Fallback to rule-based profiles if no API key
        udf = df[df['user'] != 'system']
        profiles = []
        for user in udf['user'].unique():
            grp = udf[udf['user'] == user]
            stats = _get_user_behavior_stats(grp)
            traits = _get_traits(stats)
            profile_text = f"{user} is a balanced participant most active at {stats['peak_hour']}:00."
            profiles.append({'user': user, 'profile_text': profile_text, 'traits': traits, 'stats': stats})
        return profiles

    udf = df[df['user'] != 'system']
    profiles = []

    for user in udf['user'].unique():
        grp = udf[udf['user'] == user]
        stats = _get_user_behavior_stats(grp)
        traits = _get_traits(stats)

        prompt = (
            f"Based on these messaging patterns for '{user}', write a fun 2-3 sentence "
            f"personality profile: avg {stats['avg_words']:.1f} words/msg, {stats['emoji_rate']:.1f} emojis/msg, "
            f"asks questions {stats['question_rate']:.0f}% of time, peak hour {stats['peak_hour']}:00, "
            f"night messages {stats['night_owl_pct']:.0f}%. Traits: {', '.join(traits)}. "
            f"Be playful and creative."
        )

        try:
            response = _model.generate_content(_SYSTEM_PROMPT + prompt)
            profile_text = response.text
        except Exception:
            profile_text = f"Messaging enthusiast with a peak activity at {stats['peak_hour']}:00."

        profiles.append({
            'user': user,
            'profile_text': profile_text,
            'traits': traits,
            'stats': stats,
        })

    return profiles

def _get_user_behavior_stats(grp):
    total = len(grp)
    words = grp['word_count'].mean()
    emojis_per = sum(1 for msg in grp['message'] for c in str(msg)
                     if c in __import__('emoji').EMOJI_DATA) / max(total, 1)
    questions = grp['message'].str.contains(r'\?', na=False).sum() / max(total, 1)
    hour_mode = grp['hour'].mode().iloc[0] if not grp['hour'].mode().empty else 12
    night_pct = len(grp[grp['hour'].isin([0, 1, 2, 3])]) / max(total, 1)
    
    return {
        'avg_words': round(words, 1),
        'emoji_rate': round(emojis_per, 2),
        'question_rate': round(questions * 100, 1),
        'peak_hour': int(hour_mode),
        'night_owl_pct': round(night_pct * 100, 1),
    }

def _get_traits(stats):
    traits = []
    if stats['avg_words'] > 15: traits.append('Verbose')
    elif stats['avg_words'] < 5: traits.append('Concise')
    if stats['emoji_rate'] > 1.2: traits.append('Emoji Lover')
    if stats['question_rate'] > 20: traits.append('Inquisitive')
    if stats['night_owl_pct'] > 20: traits.append('Night Owl 🌙')
    if not traits: traits.append('Steady Communicator')
    return traits
