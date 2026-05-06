import pandas as pd
import re

def detect_format(data):
    android_pattern = r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2}\s-\s'
    ios_pattern = r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[AP]M\]'
    if re.search(ios_pattern, data):
        return 'ios'
    return 'android'

def preprocess(data):
    data = data.replace('\u200e', '').replace('\ufeff', '')
    fmt = detect_format(data)

    if fmt == 'ios':
        pattern = r'\[(\d{1,2}/\d{1,2}/\d{2,4}),\s(\d{1,2}:\d{2}:\d{2}\s[AP]M)\]\s'
        parts = re.split(pattern, data)
        parts = parts[1:]
        dates_day = parts[0::3]
        dates_time = parts[1::3]
        messages = parts[2::3]
        raw_dates = [f"{d}, {t}" for d, t in zip(dates_day, dates_time)]
    else:
        pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2})\s-\s'
        split_data = re.split(pattern, data, flags=re.MULTILINE)
        split_data = split_data[1:]
        raw_dates = split_data[0::2]
        messages = split_data[1::2]

    if len(raw_dates) != len(messages):
        print("Parsing mismatch detected")
        return None

    df = pd.DataFrame({"raw_date": raw_dates, "raw_message": messages})

    if fmt == 'ios':
        df['date'] = pd.to_datetime(df['raw_date'], format='%d/%m/%Y, %I:%M:%S %p', errors='coerce')
        if df['date'].isnull().sum() > 0:
            df['date'] = pd.to_datetime(df['raw_date'], format='%d/%m/%y, %I:%M:%S %p', errors='coerce')
    else:
        df['date'] = pd.to_datetime(df['raw_date'], format='%d/%m/%Y, %H:%M', errors='coerce')
        if df['date'].isnull().sum() > 0:
            df['date'] = pd.to_datetime(df['raw_date'], format='%d/%m/%y, %H:%M', errors='coerce')

    df = df.dropna(subset=['date'])

    users, messages_clean = [], []
    for msg in df['raw_message']:
        if ':' in msg:
            user, text = msg.split(':', 1)
            users.append(user.strip())
            messages_clean.append(text.strip())
        else:
            users.append("group_notification")
            messages_clean.append(msg.strip())

    df['user'] = users
    df['message'] = messages_clean
    df['chat_format'] = fmt

    df['year'] = df['date'].dt.year
    df['only_date'] = df['date'].dt.date
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    period = []
    for hour in df['hour']:
        next_hour = (hour + 1) % 24
        period.append(f"{hour:02d}-{next_hour:02d}")
    df['period'] = period

    df.drop(columns=['raw_date', 'raw_message'], inplace=True)
    return df