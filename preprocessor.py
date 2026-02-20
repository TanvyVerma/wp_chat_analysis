import pandas as pd
import re

def preprocess(data):

    # Remove invisible encoding characters
    data = data.replace('\u200e', '').replace('\ufeff', '')

    # Pattern for 24-hour WhatsApp Android format
    # Example: 14/2/2024, 14:35 - Tanvy: Hello
    pattern = r'^(\d{1,2}/\d{1,2}/\d{2,4},\s\d{2}:\d{2})\s-\s'

    # Split using MULTILINE flag
    split_data = re.split(pattern, data, flags=re.MULTILINE)

    # First element will be empty text before first match
    split_data = split_data[1:]

    # Dates and messages aligned properly
    dates = split_data[0::2]
    messages = split_data[1::2]

    # Safety check
    if len(dates) != len(messages):
        print("⚠ Parsing mismatch detected")
        return None

    # Create dataframe
    df = pd.DataFrame({
        "raw_date": dates,
        "raw_message": messages
    })

    # Convert to datetime (Flexible year handling)
    df['date'] = pd.to_datetime(
        df['raw_date'],
        format='%d/%m/%Y, %H:%M',
        errors='coerce'
    )

    # If year is 2-digit, try alternate format
    if df['date'].isnull().sum() > 0:
        df['date'] = pd.to_datetime(
            df['raw_date'],
            format='%d/%m/%y, %H:%M',
            errors='coerce'
        )

    # Drop rows where date parsing failed
    df = df.dropna(subset=['date'])

    # Extract user and message
    users = []
    messages_clean = []

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

    # Date Feature Engineering
    df['year'] = df['date'].dt.year
    df['only_date'] = df['date'].dt.date
    df['month'] = df['date'].dt.month_name()
    df['month_num'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['day_name'] = df['date'].dt.day_name()
    df['hour'] = df['date'].dt.hour
    df['minute'] = df['date'].dt.minute

    # Create hourly period column
    period = []
    for hour in df['hour']:
        next_hour = (hour + 1) % 24
        period.append(f"{hour:02d}-{next_hour:02d}")

    df['period'] = period

    # Drop raw columns
    df.drop(columns=['raw_date', 'raw_message'], inplace=True)

    return df