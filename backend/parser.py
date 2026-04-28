"""
WhatsApp Chat Parser — robust, multi-format parser for WhatsApp chat exports.
Handles Android/iOS, 12h/24h, all date formats, Unicode LTR markers, multi-line messages.
"""

import re
import pandas as pd
from datetime import datetime
from dateutil import parser as dateutil_parser

# Regex patterns for various WhatsApp export formats
PATTERNS = [
    # Android 24h: 19/03/2025, 22:08 - Name: message
    (r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2})\s-\s', 'android_24'),
    # Android 12h: 19/03/2025, 10:08 PM - Name: message
    (r'(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}\s?[APap][Mm])\s-\s', 'android_12'),
    # iOS with seconds: [19/03/2025, 22:08:45] Name: message
    (r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2})\]\s', 'ios_24'),
    # iOS 12h with seconds: [19/03/2025, 10:08:45 PM] Name: message
    (r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}\s?[APap][Mm])\]\s', 'ios_12'),
    # US format: March 19, 2025 at 10:08 PM -
    (r'(\w+ \d{1,2},\s\d{4})\sat\s(\d{1,2}:\d{2}\s?[APap][Mm])\s-\s', 'us_format'),
    # Android with dash-date: 19-03-2025, 22:08 - Name: message
    (r'(\d{1,2}-\d{1,2}-\d{2,4}),\s(\d{1,2}:\d{2})\s-\s', 'android_dash_24'),
    # Android dot-date: 19.03.2025, 22:08 - Name: message
    (r'(\d{1,2}\.\d{1,2}\.\d{2,4}),\s(\d{1,2}:\d{2})\s-\s', 'android_dot_24'),
]

# Date format strings for parsing
DATE_FORMATS = {
    'android_24': ['%d/%m/%Y', '%m/%d/%Y', '%d/%m/%y', '%m/%d/%y'],
    'android_12': ['%d/%m/%Y', '%m/%d/%Y', '%d/%m/%y', '%m/%d/%y'],
    'ios_24': ['%d/%m/%Y', '%m/%d/%Y', '%d/%m/%y', '%m/%d/%y'],
    'ios_12': ['%d/%m/%Y', '%m/%d/%Y', '%d/%m/%y', '%m/%d/%y'],
    'us_format': ['%B %d, %Y'],
    'android_dash_24': ['%d-%m-%Y', '%m-%d-%Y', '%d-%m-%y', '%m-%d-%y'],
    'android_dot_24': ['%d.%m.%Y', '%m.%d.%Y', '%d.%m.%y', '%m.%d.%y'],
}

TIME_FORMATS_24 = ['%H:%M', '%H:%M:%S']
TIME_FORMATS_12 = ['%I:%M %p', '%I:%M%p', '%I:%M:%S %p', '%I:%M:%S%p']


def _strip_unicode_markers(content: str) -> str:
    """Remove Unicode LTR/RTL markers and other invisible chars."""
    markers = ['\u200e', '\u200f', '\u202a', '\u202c', '\u200b',
               '\u200d', '\u2069', '\u2066', '\ufeff']
    for m in markers:
        content = content.replace(m, '')
    return content


def _detect_format(content: str):
    """Auto-detect the WhatsApp export format from content."""
    for pattern, fmt_name in PATTERNS:
        if re.search(pattern, content):
            return pattern, fmt_name
    return None, None


def _parse_datetime(date_str: str, time_str: str, fmt_name: str) -> datetime:
    """Parse a date+time string pair into a datetime object."""
    time_str = time_str.strip()
    is_12h = fmt_name.endswith('_12') or fmt_name == 'us_format'

    time_formats = TIME_FORMATS_12 if is_12h else TIME_FORMATS_24
    date_formats = DATE_FORMATS.get(fmt_name, ['%d/%m/%Y'])

    for dfmt in date_formats:
        for tfmt in time_formats:
            try:
                dt = datetime.strptime(f"{date_str} {time_str}", f"{dfmt} {tfmt}")
                # Sanity check: year should be reasonable
                if 2000 <= dt.year <= 2099:
                    return dt
            except ValueError:
                continue

    # Fallback to dateutil
    try:
        return dateutil_parser.parse(f"{date_str} {time_str}", dayfirst=True)
    except Exception:
        pass

    # Last resort
    try:
        return dateutil_parser.parse(f"{date_str} {time_str}", dayfirst=False)
    except Exception:
        return None


def _detect_date_order(content: str, pattern: str, fmt_name: str):
    """Detect whether dates are DD/MM or MM/DD by analyzing all dates."""
    matches = re.findall(pattern, content)
    if not matches:
        return DATE_FORMATS.get(fmt_name, ['%d/%m/%Y'])[0]

    # Check if any date part > 12 (must be day, not month)
    date_formats = DATE_FORMATS.get(fmt_name, ['%d/%m/%Y'])
    if fmt_name == 'us_format':
        return date_formats[0]

    sep = '/' if '/' in date_formats[0] else ('-' if '-' in date_formats[0] else '.')

    for date_str, _ in matches[:50]:
        parts = date_str.split(sep)
        if len(parts) >= 2:
            try:
                first = int(parts[0])
                second = int(parts[1])
                if first > 12:
                    return date_formats[0]  # DD/MM
                if second > 12:
                    return date_formats[1] if len(date_formats) > 1 else date_formats[0]  # MM/DD
            except ValueError:
                continue

    # Default to DD/MM (most common worldwide)
    return date_formats[0]


def parse_chat(file_content: str) -> pd.DataFrame:
    """
    Parse WhatsApp chat export text into a clean DataFrame.
    Handles Android/iOS, 12h/24h, all date formats, Unicode LTR markers.

    Returns DataFrame with columns:
    [datetime, date, year, month, month_num, day, day_name, hour, minute,
     user, message, is_media, is_deleted, is_edited, is_notification,
     word_count, char_count, urls, has_url]
    """
    content = _strip_unicode_markers(file_content)

    # Auto-detect format
    pattern, fmt_name = _detect_format(content)
    if not pattern:
        raise ValueError(
            "Unrecognized WhatsApp export format. "
            "Please ensure the file is a valid WhatsApp chat export (.txt)."
        )

    # Split content into message blocks
    splits = re.split(f'({pattern})', content)

    records = []
    i = 0
    while i < len(splits):
        part = splits[i].strip()
        if not part:
            i += 1
            continue

        # Check if this part matches the date pattern start
        match = re.match(pattern, part + ' ')
        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            # The message body is what follows after the pattern match
            body = part[match.end():]
            i += 1

            # Collect continuation lines (multi-line messages)
            while i < len(splits):
                next_part = splits[i]
                if re.match(pattern, next_part + ' '):
                    break
                # Check if this is a captured group from the split
                if re.fullmatch(r'\d{1,2}[/\-.]\d{1,2}[/\-.]\d{2,4}', next_part.strip()):
                    break
                if re.fullmatch(r'\d{1,2}:\d{2}(?::\d{2})?(?:\s?[APap][Mm])?', next_part.strip()):
                    i += 1
                    continue
                if not next_part.strip():
                    i += 1
                    continue
                body += '\n' + next_part
                i += 1

            body = body.strip()
            if body:
                records.append((date_str, time_str, body))
        else:
            i += 1

    # If the simple split approach didn't work well, use finditer
    if len(records) < 5:
        records = []
        full_pattern = pattern + r'(.+?)(?=(?:' + pattern + r')|\Z)'
        for match in re.finditer(full_pattern, content, re.DOTALL):
            date_str = match.group(1)
            time_str = match.group(2)
            body = match.group(3).strip()
            if body:
                records.append((date_str, time_str, body))

    if not records:
        raise ValueError("Could not parse any messages from the file. Please check the format.")

    # Parse records into structured data
    parsed = []
    for date_str, time_str, body in records:
        dt = _parse_datetime(date_str, time_str, fmt_name)
        if dt is None:
            continue

        # Split user:message — user is before the first ": "
        colon_idx = body.find(': ')
        if colon_idx != -1 and colon_idx < 80:
            user = body[:colon_idx].strip()
            message = body[colon_idx + 2:].strip()
        else:
            # System notification (no colon separator)
            user = 'system'
            message = body

        parsed.append({
            'datetime': dt,
            'user': user,
            'message': message,
        })

    if not parsed:
        raise ValueError("Could not parse any messages. Please check the file format.")

    df = pd.DataFrame(parsed)

    # Ensure datetime is proper type
    df['datetime'] = pd.to_datetime(df['datetime'])
    df = df.sort_values('datetime').reset_index(drop=True)

    # Derived date columns
    df['date'] = df['datetime'].dt.date
    df['year'] = df['datetime'].dt.year
    df['month'] = df['datetime'].dt.month_name()
    df['month_num'] = df['datetime'].dt.month
    df['day'] = df['datetime'].dt.day
    df['day_name'] = df['datetime'].dt.day_name()
    df['hour'] = df['datetime'].dt.hour
    df['minute'] = df['datetime'].dt.minute

    # Content analysis columns
    df['is_media'] = df['message'].str.contains(
        r'<Media omitted>|<media omitted>|image omitted|video omitted|audio omitted|'
        r'sticker omitted|GIF omitted|Contact card omitted|document omitted|'
        r'<View once voice message omitted>|<View once photo omitted>',
        case=False, na=False, regex=True
    )
    df['is_deleted'] = df['message'].str.contains(
        r'This message was deleted|You deleted this message|'
        r'this message was deleted|you deleted this message',
        na=False, regex=True
    )
    df['is_edited'] = df['message'].str.contains(
        '<This message was edited>', na=False
    )
    # System/notification messages (no colon in original, or system user)
    df['is_notification'] = df['user'].str.lower() == 'system'

    # Word and char counts (for actual messages, not media/deleted/system)
    df['word_count'] = df.apply(
        lambda row: len(str(row['message']).split())
        if not (row['is_media'] or row['is_deleted'] or row['is_notification'])
        else 0, axis=1
    )
    df['char_count'] = df.apply(
        lambda row: len(str(row['message']))
        if not (row['is_media'] or row['is_deleted'] or row['is_notification'])
        else 0, axis=1
    )

    # URL extraction
    url_pattern = r'https?://[^\s<>\"\')\]]*'
    df['urls'] = df['message'].apply(lambda x: re.findall(url_pattern, str(x)))
    df['has_url'] = df['urls'].apply(lambda x: len(x) > 0)

    # Filter out system notifications from main analysis but keep them in DF
    return df


def get_users(df: pd.DataFrame) -> list:
    """Get list of unique non-system users."""
    return sorted(df[df['user'] != 'system']['user'].unique().tolist())
