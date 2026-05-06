import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect as lang_detect, LangDetectException
import numpy as np
from fpdf import FPDF
import matplotlib.pyplot as plt
import io
import tempfile
import os

extract = URLExtract()
analyzer = SentimentIntensityAnalyzer()


# ── FETCH STATS ──────────────────────────────────────────────────────────────
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    num_msg = df.shape[0]
    words = []
    for message in df['message']:
        words.extend(message.split())
    num_media = df[df['message'] == '<Media omitted>'].shape[0]
    links = []
    for message in df['message']:
        links.extend(extract.find_urls(message))
    return num_msg, len(words), num_media, len(links)


# ── MOST BUSY USERS ───────────────────────────────────────────────────────────
def most_busy_users(df):
    x = df['user'].value_counts().head()
    percent_df = round(
        (df['user'].value_counts() / df.shape[0]) * 100, 2
    ).reset_index().rename(columns={'index': 'name', 'user': 'percent'})
    return x, percent_df


# ── WORDCLOUD ─────────────────────────────────────────────────────────────────
def create_wordcloud(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()

    def remove_stop_words(message):
        return " ".join(word for word in message.lower().split() if word not in stop_words)

    temp['message'] = temp['message'].apply(remove_stop_words)
    wc = WordCloud(width=500, height=500, min_font_size=10, background_color='white')
    return wc.generate(temp['message'].str.cat(sep=' '))


# ── MOST COMMON WORDS ─────────────────────────────────────────────────────────
def most_common_words(selected_user, df):
    with open('stop_hinglish.txt', 'r') as f:
        stop_words = f.read()
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    temp = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ]
    words = []
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    return pd.DataFrame(Counter(words).most_common(20))


# ── EMOJI ANALYSIS ────────────────────────────────────────────────────────────
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if emoji.is_emoji(c)])
    return pd.DataFrame(Counter(emojis).most_common())


# ── MONTHLY TIMELINE ──────────────────────────────────────────────────────────
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    timeline = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    timeline['time'] = timeline['month'] + '-' + timeline['year'].astype(str)
    return timeline


# ── DAILY TIMELINE ────────────────────────────────────────────────────────────
def daily_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.groupby('only_date').count()['message'].reset_index()


# ── WEEK ACTIVITY ─────────────────────────────────────────────────────────────
def week_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['day_name'].value_counts()


# ── MONTH ACTIVITY ────────────────────────────────────────────────────────────
def month_activity_map(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df['month'].value_counts()


# ── HEATMAP ───────────────────────────────────────────────────────────────────
def activity_heatmap(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    return df.pivot_table(
        index='day_name', columns='period',
        values='message', aggfunc='count'
    ).fillna(0)


# ── SENTIMENT ANALYSIS ────────────────────────────────────────────────────────
def get_sentiment_score(message):
    score = analyzer.polarity_scores(message)
    return score['compound']

def classify_sentiment(score):
    if score >= 0.05:
        return 'Positive'
    elif score <= -0.05:
        return 'Negative'
    else:
        return 'Neutral'

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()
    df['sentiment_score'] = df['message'].apply(get_sentiment_score)
    df['sentiment'] = df['sentiment_score'].apply(classify_sentiment)
    return df

def daily_sentiment_trend(selected_user, df):
    df = sentiment_analysis(selected_user, df)
    trend = df.groupby('only_date')['sentiment_score'].mean().reset_index()
    trend.columns = ['date', 'avg_sentiment']
    trend['rolling_avg'] = trend['avg_sentiment'].rolling(window=7, min_periods=1).mean()
    return trend

def user_sentiment_summary(df):
    users = df['user'].unique().tolist()
    if 'group_notification' in users:
        users.remove('group_notification')
    summary = []
    for user in users:
        user_df = df[df['user'] == user].copy()
        user_df['score'] = user_df['message'].apply(get_sentiment_score)
        avg = user_df['score'].mean()
        summary.append({'user': user, 'avg_sentiment': round(avg, 3)})
    return pd.DataFrame(summary).sort_values('avg_sentiment', ascending=False)

def sentiment_counts(selected_user, df):
    df = sentiment_analysis(selected_user, df)
    return df['sentiment'].value_counts()


# ── RESPONSE TIME ANALYSIS ────────────────────────────────────────────────────
def response_time_analysis(df):
    df = df[df['user'] != 'group_notification'].copy()
    df = df.sort_values('date').reset_index(drop=True)

    response_times = []
    for i in range(1, len(df)):
        if df.loc[i, 'user'] != df.loc[i-1, 'user']:
            delta = (df.loc[i, 'date'] - df.loc[i-1, 'date']).total_seconds() / 60
            if 0 < delta < 1440:  # ignore gaps longer than 24 hours
                response_times.append({
                    'responder': df.loc[i, 'user'],
                    'response_time_min': round(delta, 2)
                })

    rt_df = pd.DataFrame(response_times)
    if rt_df.empty:
        return rt_df, pd.DataFrame()

    avg_rt = rt_df.groupby('responder')['response_time_min'].mean().round(2).reset_index()
    avg_rt.columns = ['user', 'avg_response_time_min']
    avg_rt = avg_rt.sort_values('avg_response_time_min')
    return rt_df, avg_rt

def longest_silence(df):
    df = df[df['user'] != 'group_notification'].copy()
    df = df.sort_values('date').reset_index(drop=True)
    max_gap = 0
    gap_start = gap_end = None
    for i in range(1, len(df)):
        delta = (df.loc[i, 'date'] - df.loc[i-1, 'date']).total_seconds() / 3600
        if delta > max_gap:
            max_gap = delta
            gap_start = df.loc[i-1, 'date']
            gap_end = df.loc[i, 'date']
    return round(max_gap, 1), gap_start, gap_end


# ── CONVERSATION STREAKS ──────────────────────────────────────────────────────
def conversation_streaks(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    active_days = pd.to_datetime(df['only_date'].unique())
    active_days = sorted(active_days)

    if not active_days:
        return 0, 0, []

    streaks = []
    current_streak = 1
    max_streak = 1

    for i in range(1, len(active_days)):
        diff = (active_days[i] - active_days[i-1]).days
        if diff == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            streaks.append(current_streak)
            current_streak = 1

    streaks.append(current_streak)

    # Current streak from today backwards
    today = pd.Timestamp.now().normalize()
    curr = 0
    for day in reversed(active_days):
        expected = today - pd.Timedelta(days=curr)
        if day == expected:
            curr += 1
        else:
            break

    return max_streak, curr, streaks


# ── LANGUAGE DETECTION ────────────────────────────────────────────────────────
def language_distribution(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()

    def safe_detect(text):
        try:
            if len(text.strip()) < 10:
                return 'unknown'
            return lang_detect(text)
        except LangDetectException:
            return 'unknown'

    df['language'] = df['message'].apply(safe_detect)
    lang_counts = df['language'].value_counts().reset_index()
    lang_counts.columns = ['language', 'count']
    return lang_counts


# ── TOPIC MODELING ────────────────────────────────────────────────────────────
def topic_modeling(selected_user, df, num_topics=5):
    try:
        from gensim import corpora
        from gensim.models import LdaModel
        from gensim.parsing.preprocessing import STOPWORDS
    except ImportError:
        return None, "Install gensim: pip install gensim"

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()

    with open('stop_hinglish.txt', 'r') as f:
        custom_stops = set(f.read().split())

    all_stops = STOPWORDS.union(custom_stops)

    def tokenize(text):
        return [
            word for word in text.lower().split()
            if word not in all_stops and len(word) > 3
        ]

    texts = [tokenize(msg) for msg in df['message']]
    texts = [t for t in texts if len(t) > 0]

    if len(texts) < 10:
        return None, "Not enough messages for topic modeling"

    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=2, no_above=0.9)
    corpus = [dictionary.doc2bow(text) for text in texts]

    lda = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        random_state=42,
        passes=10
    )

    topics = []
    for i, topic in lda.show_topics(formatted=False, num_words=8):
        words = [word for word, _ in topic]
        topics.append({'topic': f'Topic {i+1}', 'keywords': ', '.join(words)})

    return pd.DataFrame(topics), None


# ── PDF REPORT EXPORT ─────────────────────────────────────────────────────────
def save_fig_to_temp(fig):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    fig.savefig(tmp.name, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return tmp.name

def generate_pdf_report(selected_user, df):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 12, 'WhatsApp Chat Analysis Report', ln=True, align='C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'User: {selected_user}', ln=True, align='C')
    pdf.ln(6)

    # Stats
    num_msg, num_word, num_media, num_links = fetch_stats(selected_user, df)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Key Statistics', ln=True)
    pdf.set_font('Arial', '', 12)
    stats = [
        ('Total Messages', num_msg),
        ('Total Words', num_word),
        ('Media Shared', num_media),
        ('Links Shared', num_links),
    ]
    for label, val in stats:
        pdf.cell(0, 8, f'  {label}: {val}', ln=True)
    pdf.ln(4)

    # Sentiment summary
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Sentiment Summary', ln=True)
    pdf.set_font('Arial', '', 12)
    counts = sentiment_counts(selected_user, df)
    for sentiment, count in counts.items():
        pdf.cell(0, 8, f'  {sentiment}: {count} messages', ln=True)
    pdf.ln(4)

    # Monthly timeline chart
    timeline = monthly_timeline(selected_user, df)
    if not timeline.empty:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(timeline['time'], timeline['message'], marker='o')
        ax.set_title('Monthly Timeline')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = save_fig_to_temp(fig)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Monthly Timeline', ln=True)
        pdf.image(path, w=180)
        os.unlink(path)
        pdf.ln(4)

    # Sentiment trend chart
    trend = daily_sentiment_trend(selected_user, df)
    if not trend.empty:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(trend['date'], trend['rolling_avg'], color='green')
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax.set_title('Sentiment Trend (7-day rolling avg)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = save_fig_to_temp(fig)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Sentiment Trend', ln=True)
        pdf.image(path, w=180)
        os.unlink(path)

    # Output as bytes
    return bytes(pdf.output())