"""
WhatsApp Chat Analyzer — all analysis functions.
Each returns JSON-serializable Python dicts/lists.
"""

import pandas as pd
import numpy as np
from collections import Counter
import emoji
import re
import os
from urllib.parse import urlparse
from datetime import timedelta

# Load stopwords once
_STOPWORDS = set()
_stop_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stop_hinglish.txt')
if os.path.exists(_stop_path):
    with open(_stop_path, 'r', encoding='utf-8') as f:
        _STOPWORDS = set(line.strip().lower() for line in f if line.strip())


def _filter_users(df, user=None):
    """Filter DataFrame to non-system messages, optionally by user."""
    filtered = df[df['user'] != 'system'].copy()
    if user and user != 'all':
        filtered = filtered[filtered['user'] == user]
    return filtered


def _extract_emojis(text):
    """Extract all emojis from text."""
    return [c for c in str(text) if c in emoji.EMOJI_DATA]


def get_overview_stats(df):
    udf = df[df['user'] != 'system']
    date_range = (udf['datetime'].max() - udf['datetime'].min()).days + 1 if len(udf) > 1 else 1
    most_active = udf.groupby('date').size()
    mad = most_active.idxmax() if len(most_active) > 0 else None
    mad_count = int(most_active.max()) if len(most_active) > 0 else 0

    # Peak conversation date details
    total_urls = int(udf['has_url'].sum())
    total_media = int(udf['is_media'].sum())

    # Message velocity - messages per hour during peak day
    peak_velocity = 0
    if mad:
        peak_day = udf[udf['date'] == mad]
        hours_active = peak_day['hour'].nunique()
        peak_velocity = round(len(peak_day) / max(hours_active, 1), 1)

    # Silent days
    if len(udf) > 1:
        all_dates = pd.date_range(udf['datetime'].min().date(), udf['datetime'].max().date())
        active_dates = set(udf['date'].unique())
        silent_days = len(all_dates) - len(active_dates)
    else:
        silent_days = 0

    return {
        'total_messages': int(len(udf)),
        'total_words': int(udf['word_count'].sum()),
        'total_media': total_media,
        'total_links': total_urls,
        'total_deleted': int(udf['is_deleted'].sum()),
        'total_edited': int(udf['is_edited'].sum()),
        'date_range_days': date_range,
        'first_message_date': str(udf['datetime'].min().date()) if len(udf) > 0 else '',
        'last_message_date': str(udf['datetime'].max().date()) if len(udf) > 0 else '',
        'most_active_day': str(mad) if mad else '',
        'most_active_day_count': mad_count,
        'total_unique_users': int(udf['user'].nunique()),
        'peak_velocity': peak_velocity,
        'silent_days': silent_days,
        'avg_messages_per_day': round(len(udf) / max(date_range, 1), 1),
    }


def get_user_stats(df):
    udf = df[df['user'] != 'system']
    total = len(udf)
    results = []
    avg_msgs = total / max(udf['user'].nunique(), 1)

    for user, grp in udf.groupby('user'):
        all_emojis = []
        for msg in grp['message']:
            all_emojis.extend(_extract_emojis(msg))

        # Questions asked
        questions = grp['message'].str.contains(r'\?', na=False).sum()

        # CAPS messages (>3 words, >70% caps)
        def is_caps(msg):
            words = str(msg).split()
            if len(words) < 3:
                return False
            alpha = ''.join(c for c in str(msg) if c.isalpha())
            if not alpha:
                return False
            return sum(1 for c in alpha if c.isupper()) / len(alpha) > 0.7
        caps_count = int(grp['message'].apply(is_caps).sum())

        # Longest streak
        dates = sorted(grp['date'].unique())
        max_streak = 1
        current_streak = 1
        for i in range(1, len(dates)):
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        if len(dates) == 0:
            max_streak = 0

        # Most active hour
        hour_counts = grp['hour'].value_counts()
        most_active_hour = int(hour_counts.index[0]) if len(hour_counts) > 0 else 0

        # First and last message text
        first_msg = grp.iloc[0]['message'] if len(grp) > 0 else ''
        last_msg = grp.iloc[-1]['message'] if len(grp) > 0 else ''
        if len(first_msg) > 100:
            first_msg = first_msg[:100] + '...'
        if len(last_msg) > 100:
            last_msg = last_msg[:100] + '...'

        results.append({
            'name': user,
            'message_count': int(len(grp)),
            'message_pct': round(len(grp) / max(total, 1) * 100, 1),
            'word_count': int(grp['word_count'].sum()),
            'avg_words_per_msg': round(grp['word_count'].mean(), 1) if len(grp) > 0 else 0,
            'media_count': int(grp['is_media'].sum()),
            'link_count': int(grp['has_url'].sum()),
            'deleted_count': int(grp['is_deleted'].sum()),
            'edited_count': int(grp['is_edited'].sum()),
            'emoji_count': len(all_emojis),
            'first_message_date': str(grp['datetime'].min().date()),
            'last_message_date': str(grp['datetime'].max().date()),
            'most_active_hour': most_active_hour,
            'questions_asked': int(questions),
            'caps_messages': caps_count,
            'longest_streak': max_streak,
            'first_message_text': first_msg,
            'last_message_text': last_msg,
        })

    results.sort(key=lambda x: x['message_count'], reverse=True)
    return results


def get_timeline_data(df, granularity='daily', user=None):
    udf = _filter_users(df, user)
    if len(udf) == 0:
        return {'labels': [], 'datasets': []}

    if granularity == 'monthly':
        udf = udf.copy()
        udf['period'] = udf['datetime'].dt.to_period('M').astype(str)
    elif granularity == 'weekly':
        udf = udf.copy()
        udf['period'] = udf['datetime'].dt.to_period('W').astype(str)
    else:
        udf = udf.copy()
        udf['period'] = udf['date'].astype(str)

    if user and user != 'all':
        counts = udf.groupby('period').size().reset_index(name='count')
        labels = counts['period'].tolist()
        return {
            'labels': labels,
            'datasets': [{'user': user, 'data': counts['count'].tolist()}]
        }

    pivot = udf.groupby(['period', 'user']).size().unstack(fill_value=0)
    labels = pivot.index.tolist()
    datasets = []
    for col in pivot.columns:
        datasets.append({'user': col, 'data': pivot[col].tolist()})

    return {'labels': labels, 'datasets': datasets}


def get_activity_heatmap(df):
    udf = df[df['user'] != 'system']
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hours = list(range(24))
    data = []
    for day in days:
        row = []
        for hour in hours:
            count = int(len(udf[(udf['day_name'] == day) & (udf['hour'] == hour)]))
            row.append(count)
        data.append(row)
    return {'days': days, 'hours': hours, 'data': data}


def get_word_frequency(df, user=None, top_n=30):
    udf = _filter_users(df, user)
    udf = udf[~udf['is_media'] & ~udf['is_deleted'] & ~udf['is_notification']]

    all_words = []
    url_pat = re.compile(r'https?://\S+')
    phone_pat = re.compile(r'@?\d{10,}')
    num_pat = re.compile(r'^\d+$')

    for msg in udf['message']:
        text = str(msg).lower()
        text = url_pat.sub('', text)
        text = phone_pat.sub('', text)
        text = text.replace('<this message was edited>', '')
        text = text.replace('<media omitted>', '')
        # Remove emojis
        text = ''.join(c for c in text if c not in emoji.EMOJI_DATA)
        words = re.findall(r'[a-zA-Z\u0900-\u097F]{2,}', text)
        for w in words:
            w = w.lower().strip()
            if w and w not in _STOPWORDS and not num_pat.match(w) and len(w) > 1:
                all_words.append(w)

    freq = Counter(all_words).most_common(top_n)
    return [{'word': w, 'count': c} for w, c in freq]


def get_emoji_stats(df, user=None):
    udf = _filter_users(df, user)
    all_emojis = []
    for msg in udf['message']:
        all_emojis.extend(_extract_emojis(msg))

    freq = Counter(all_emojis).most_common(20)
    results = []
    for e, c in freq:
        name = emoji.demojize(e, delimiters=('', ''))
        results.append({'emoji': e, 'name': name, 'count': c})
    return results


def get_response_time_stats(df):
    udf = df[(df['user'] != 'system') & ~df['is_notification']].sort_values('datetime').reset_index(drop=True)
    if len(udf) < 2:
        return {'per_user': {}, 'overall_pace': {}}

    user_times = {}
    for i in range(1, len(udf)):
        curr = udf.iloc[i]
        prev = udf.iloc[i - 1]
        if curr['user'] != prev['user']:
            diff = (curr['datetime'] - prev['datetime']).total_seconds() / 60
            if 0 < diff <= 1440:  # Max 24h gap
                user_times.setdefault(curr['user'], []).append(diff)

    per_user = {}
    for u, times in user_times.items():
        per_user[u] = {
            'avg_minutes': round(np.mean(times), 1),
            'median_minutes': round(float(np.median(times)), 1),
            'fastest_reply_minutes': round(min(times), 1),
            'total_replies': len(times),
        }

    # Pace buckets
    all_times = [t for times in user_times.values() for t in times]
    pace = {'under_1min': 0, '1_5min': 0, '5_30min': 0, '30_60min': 0, 'over_1hr': 0}
    for t in all_times:
        if t < 1: pace['under_1min'] += 1
        elif t < 5: pace['1_5min'] += 1
        elif t < 30: pace['5_30min'] += 1
        elif t < 60: pace['30_60min'] += 1
        else: pace['over_1hr'] += 1

    return {'per_user': per_user, 'overall_pace': pace}


def get_conversation_starters(df):
    udf = df[(df['user'] != 'system') & ~df['is_notification']].sort_values('datetime').reset_index(drop=True)
    if len(udf) == 0:
        return []

    starters = []
    starters.append(udf.iloc[0]['user'])  # First message is always a starter

    for i in range(1, len(udf)):
        gap = (udf.iloc[i]['datetime'] - udf.iloc[i - 1]['datetime']).total_seconds() / 3600
        if gap >= 4:
            starters.append(udf.iloc[i]['user'])

    counts = Counter(starters)
    total = sum(counts.values())
    return [
        {'user': u, 'count': c, 'pct': round(c / max(total, 1) * 100, 1)}
        for u, c in counts.most_common()
    ]


def get_url_analysis(df):
    udf = df[df['user'] != 'system']
    all_urls = []
    for urls in udf['urls']:
        all_urls.extend(urls)

    if not all_urls:
        return {'total_urls': 0, 'top_domains': [], 'platform_breakdown': {}, 'recent_urls': []}

    domains = []
    platform_map = {
        'youtube.com': 'YouTube', 'youtu.be': 'YouTube',
        'instagram.com': 'Instagram',
        'twitter.com': 'Twitter', 'x.com': 'Twitter',
        'facebook.com': 'Facebook', 'fb.com': 'Facebook',
        'reddit.com': 'Reddit',
        'spotify.com': 'Spotify', 'open.spotify.com': 'Spotify',
        'tiktok.com': 'TikTok',
        'linkedin.com': 'LinkedIn',
        'amazon.in': 'Amazon', 'amazon.com': 'Amazon', 'amzn.in': 'Amazon',
        'flipkart.com': 'Flipkart',
        'github.com': 'GitHub',
    }
    platforms = Counter()

    for url in all_urls:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '').lower()
            domains.append(domain)
            for key, platform in platform_map.items():
                if key in domain:
                    platforms[platform] += 1
                    break
            else:
                platforms['Other'] += 1
        except Exception:
            pass

    domain_counts = Counter(domains).most_common(15)
    return {
        'total_urls': len(all_urls),
        'top_domains': [{'domain': d, 'count': c} for d, c in domain_counts],
        'platform_breakdown': dict(platforms.most_common()),
    }


def get_sentiment_over_time(df):
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
    except ImportError:
        return {'labels': [], 'datasets': [], 'error': 'vaderSentiment not installed'}

    udf = df[(df['user'] != 'system') & ~df['is_media'] & ~df['is_deleted']].copy()
    if len(udf) == 0:
        return {'labels': [], 'datasets': []}

    udf['week'] = udf['datetime'].dt.to_period('W').astype(str)

    def get_sentiment(text):
        try:
            # Only analyze if text has enough ASCII/latin chars
            ascii_chars = sum(1 for c in str(text) if c.isascii() and c.isalpha())
            if ascii_chars < 3:
                return 0.0
            return analyzer.polarity_scores(str(text))['compound']
        except Exception:
            return 0.0

    udf['sentiment'] = udf['message'].apply(get_sentiment)

    datasets = []
    labels = sorted(udf['week'].unique())

    for user in udf['user'].unique():
        user_data = udf[udf['user'] == user]
        weekly = user_data.groupby('week')['sentiment'].mean()
        data = [round(float(weekly.get(w, 0)), 3) for w in labels]
        datasets.append({'user': user, 'data': data})

    return {'labels': labels, 'datasets': datasets}


def get_deleted_message_analysis(df):
    udf = df[df['user'] != 'system']
    deleted = udf[udf['is_deleted']]

    if len(deleted) == 0:
        return {'total_deleted': 0, 'per_user': [], 'peak_hours': [], 'trend': {'labels': [], 'data': []}}

    per_user = []
    for user, grp in deleted.groupby('user'):
        per_user.append({'user': user, 'count': int(len(grp)),
                         'pct': round(len(grp) / max(len(udf[udf['user'] == user]), 1) * 100, 1)})
    per_user.sort(key=lambda x: x['count'], reverse=True)

    hours = deleted['hour'].value_counts().sort_index()
    peak_hours = [{'hour': int(h), 'count': int(c)} for h, c in hours.items()]

    monthly = deleted.groupby(deleted['datetime'].dt.to_period('M').astype(str)).size()
    trend = {'labels': monthly.index.tolist(), 'data': monthly.values.tolist()}

    return {'total_deleted': int(len(deleted)), 'per_user': per_user, 'peak_hours': peak_hours, 'trend': trend}


def get_media_analysis(df):
    udf = df[df['user'] != 'system']
    media = udf[udf['is_media']]

    if len(media) == 0:
        return {'total_media': 0, 'per_user': [], 'peak_hours': [], 'daily': {'labels': [], 'data': []}}

    per_user = []
    for user, grp in media.groupby('user'):
        per_user.append({'user': user, 'count': int(len(grp))})
    per_user.sort(key=lambda x: x['count'], reverse=True)

    hours = media['hour'].value_counts().sort_index()
    peak_hours = [{'hour': int(h), 'count': int(c)} for h, c in hours.items()]

    daily = media.groupby(media['date'].astype(str)).size()
    daily_data = {'labels': daily.index.tolist()[-60:], 'data': daily.values.tolist()[-60:]}

    return {'total_media': int(len(media)), 'per_user': per_user, 'peak_hours': peak_hours, 'daily': daily_data}


def get_longest_messages(df, top_n=10):
    udf = df[(df['user'] != 'system') & ~df['is_media'] & ~df['is_deleted']]
    top = udf.nlargest(top_n, 'word_count')
    results = []
    for _, row in top.iterrows():
        msg = str(row['message'])
        if len(msg) > 300:
            msg = msg[:300] + '...'
        results.append({
            'user': row['user'],
            'message': msg,
            'word_count': int(row['word_count']),
            'date': str(row['date']),
        })
    return results


def get_ghost_analysis(df):
    udf = df[df['user'] != 'system']
    avg_msgs = len(udf) / max(udf['user'].nunique(), 1)
    user_counts = udf['user'].value_counts()

    results = []
    for user, count in user_counts.items():
        if count < avg_msgs * 0.4:
            results.append({
                'user': user,
                'messages': int(count),
                'avg_messages': round(avg_msgs, 1),
                'ghost_score': round((1 - count / max(avg_msgs, 1)) * 100, 1),
            })
    results.sort(key=lambda x: x['ghost_score'], reverse=True)
    return results


def get_poll_analysis(df):
    udf = df[df['user'] != 'system']
    polls = []
    for _, row in udf.iterrows():
        msg = str(row['message'])
        if 'POLL:' in msg or msg.startswith('POLL:'):
            lines = msg.split('\n')
            title = ''
            options = []
            for line in lines:
                line = line.strip()
                if line.startswith('POLL:'):
                    title = line.replace('POLL:', '').strip()
                elif line.startswith('OPTION:'):
                    opt_text = line.replace('OPTION:', '').strip()
                    vote_match = re.search(r'\((\d+)\s*vote', opt_text)
                    votes = int(vote_match.group(1)) if vote_match else 0
                    opt_name = re.sub(r'\(\d+\s*votes?\)', '', opt_text).strip()
                    options.append({'option': opt_name, 'votes': votes})
                elif not title and line and 'OPTION:' not in line:
                    title = line

            if options:
                polls.append({
                    'user': row['user'],
                    'title': title or 'Untitled Poll',
                    'date': str(row['date']),
                    'options': options,
                    'total_votes': sum(o['votes'] for o in options),
                })
    return polls


def get_night_owl_stats(df):
    udf = df[df['user'] != 'system']
    night = udf[udf['hour'].isin([0, 1, 2, 3])]

    per_user = []
    for user in udf['user'].unique():
        user_night = night[night['user'] == user]
        user_total = udf[udf['user'] == user]
        per_user.append({
            'user': user,
            'night_messages': int(len(user_night)),
            'night_pct': round(len(user_night) / max(len(user_total), 1) * 100, 1),
            'total_messages': int(len(user_total)),
        })
    per_user.sort(key=lambda x: x['night_messages'], reverse=True)

    return {'total_night_messages': int(len(night)), 'per_user': per_user}


def get_conversation_network(df):
    udf = df[(df['user'] != 'system') & ~df['is_notification']].sort_values('datetime').reset_index(drop=True)
    if len(udf) < 2:
        return {'nodes': [], 'edges': []}

    edges = Counter()
    for i in range(1, len(udf)):
        curr = udf.iloc[i]
        prev = udf.iloc[i - 1]
        if curr['user'] != prev['user']:
            diff = (curr['datetime'] - prev['datetime']).total_seconds() / 60
            if diff <= 30:
                edges[(prev['user'], curr['user'])] += 1

    user_counts = udf['user'].value_counts()
    nodes = [{'id': u, 'label': u, 'size': int(c)} for u, c in user_counts.items()]
    edge_list = [{'from': f, 'to': t, 'weight': w} for (f, t), w in edges.most_common()]

    return {'nodes': nodes, 'edges': edge_list}


def get_late_replies(df):
    """Messages that went >12h without reply."""
    udf = df[(df['user'] != 'system') & ~df['is_notification']].sort_values('datetime').reset_index(drop=True)
    late = []
    for i in range(1, len(udf)):
        diff_h = (udf.iloc[i]['datetime'] - udf.iloc[i-1]['datetime']).total_seconds() / 3600
        if diff_h > 12:
            late.append({
                'original_user': udf.iloc[i-1]['user'],
                'original_message': str(udf.iloc[i-1]['message'])[:100],
                'reply_user': udf.iloc[i]['user'],
                'gap_hours': round(diff_h, 1),
                'date': str(udf.iloc[i]['date']),
            })
    late.sort(key=lambda x: x['gap_hours'], reverse=True)
    return late[:20]


def get_language_stats(df):
    """Estimate language distribution (Hindi vs English vs mixed)."""
    udf = df[(df['user'] != 'system') & ~df['is_media'] & ~df['is_deleted']]
    hindi_pat = re.compile(r'[\u0900-\u097F]')
    english_pat = re.compile(r'[a-zA-Z]')

    stats = {'english': 0, 'hindi': 0, 'mixed': 0, 'other': 0}
    for msg in udf['message']:
        text = str(msg)
        has_hindi = bool(hindi_pat.search(text))
        has_english = bool(english_pat.search(text))
        if has_hindi and has_english:
            stats['mixed'] += 1
        elif has_hindi:
            stats['hindi'] += 1
        elif has_english:
            stats['english'] += 1
        else:
            stats['other'] += 1

    total = sum(stats.values()) or 1
    return {k: {'count': v, 'pct': round(v / total * 100, 1)} for k, v in stats.items()}
