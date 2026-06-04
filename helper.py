import pandas as pd
from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import emoji
import numpy as np
import matplotlib.pyplot as plt
import tempfile
import os

# ── Safe VADER import ─────────────────────────────────────────────────────────
try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    analyzer = SentimentIntensityAnalyzer()
except ImportError:
    try:
        import nltk
        nltk.download('vader_lexicon', quiet=True)
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
    except Exception:
        analyzer = None

# ── Safe langdetect import ────────────────────────────────────────────────────
try:
    from langdetect import detect as lang_detect, LangDetectException
    LANGDETECT_OK = True
except ImportError:
    LANGDETECT_OK = False

# ── Safe fpdf2 import ─────────────────────────────────────────────────────────
try:
    from fpdf import FPDF
    FPDF_OK = True
except ImportError:
    FPDF_OK = False

extract = URLExtract()


# ── LOAD STOP WORDS (returns a Python set, never a DataFrame) ─────────────────
def _load_stop_words():
    try:
        with open('stop_hinglish.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        # content is one big string; split into a set of individual words
        return set(content.split())
    except FileNotFoundError:
        return set()


# ── FETCH STATS ───────────────────────────────────────────────────────────────
def fetch_stats(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    num_msg   = df.shape[0]
    words     = []
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
    stop_words = _load_stop_words()   # always a set now

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()

    if temp.empty:
        raise ValueError("No messages available to generate word cloud.")

    def remove_stop_words(message):
        return " ".join(
            word for word in str(message).lower().split()
            if word not in stop_words
        )

    temp['message'] = temp['message'].apply(remove_stop_words)

    all_text = temp['message'].str.cat(sep=' ').strip()

    if not all_text:
        raise ValueError("All words were filtered out by stop words.")

    wc = WordCloud(
        width=800,
        height=400,
        min_font_size=10,
        background_color='white',
        max_words=200,
        collocations=False
    )
    return wc.generate(all_text)


# ── MOST COMMON WORDS ─────────────────────────────────────────────────────────
def most_common_words(selected_user, df):
    stop_words = _load_stop_words()   # always a set

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    temp = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ]

    words = []
    for message in temp['message']:
        for word in str(message).lower().split():
            if word not in stop_words:
                words.append(word)

    return pd.DataFrame(Counter(words).most_common(20))


# ── EMOJI ANALYSIS ────────────────────────────────────────────────────────────
def emoji_helper(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in str(message) if emoji.is_emoji(c)])

    return pd.DataFrame(Counter(emojis).most_common())


# ── MONTHLY TIMELINE ──────────────────────────────────────────────────────────
def monthly_timeline(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    timeline = (
        df.groupby(['year', 'month_num', 'month'])
        .count()['message']
        .reset_index()
    )
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
        index='day_name',
        columns='period',
        values='message',
        aggfunc='count'
    ).fillna(0)


# ── SENTIMENT HELPERS ─────────────────────────────────────────────────────────
def _get_score(message):
    if analyzer is None:
        return 0.0
    return analyzer.polarity_scores(str(message))['compound']

def _classify(score):
    if score >= 0.05:  return 'Positive'
    if score <= -0.05: return 'Negative'
    return 'Neutral'

def sentiment_analysis(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]
    df = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()
    df['sentiment_score'] = df['message'].apply(_get_score)
    df['sentiment']       = df['sentiment_score'].apply(_classify)
    return df

def daily_sentiment_trend(selected_user, df):
    df2   = sentiment_analysis(selected_user, df)
    trend = df2.groupby('only_date')['sentiment_score'].mean().reset_index()
    trend.columns = ['date', 'avg_sentiment']
    trend['rolling_avg'] = trend['avg_sentiment'].rolling(window=7, min_periods=1).mean()
    return trend

def user_sentiment_summary(df):
    users = [u for u in df['user'].unique() if u != 'group_notification']
    rows  = []
    for user in users:
        udf = df[df['user'] == user].copy()
        udf['score'] = udf['message'].apply(_get_score)
        rows.append({'user': user, 'avg_sentiment': round(udf['score'].mean(), 3)})
    return pd.DataFrame(rows).sort_values('avg_sentiment', ascending=False).reset_index(drop=True)

def sentiment_counts(selected_user, df):
    return sentiment_analysis(selected_user, df)['sentiment'].value_counts()


# ── RESPONSE TIME ─────────────────────────────────────────────────────────────
def response_time_analysis(df):
    df2 = df[df['user'] != 'group_notification'].copy()
    df2 = df2.sort_values('date').reset_index(drop=True)

    rows = []
    for i in range(1, len(df2)):
        if df2.loc[i, 'user'] != df2.loc[i-1, 'user']:
            delta = (df2.loc[i, 'date'] - df2.loc[i-1, 'date']).total_seconds() / 60
            if 0 < delta < 1440:
                rows.append({
                    'responder':          df2.loc[i, 'user'],
                    'response_time_min':  round(delta, 2)
                })

    rt_df = pd.DataFrame(rows)
    if rt_df.empty:
        return rt_df, pd.DataFrame()

    avg_rt = (
        rt_df.groupby('responder')['response_time_min']
        .mean().round(2).reset_index()
        .rename(columns={'responder': 'user', 'response_time_min': 'avg_response_time_min'})
        .sort_values('avg_response_time_min')
        .reset_index(drop=True)
    )
    return rt_df, avg_rt

def longest_silence(df):
    df2     = df[df['user'] != 'group_notification'].copy().sort_values('date').reset_index(drop=True)
    max_gap = 0
    gap_start = gap_end = None
    for i in range(1, len(df2)):
        delta = (df2.loc[i, 'date'] - df2.loc[i-1, 'date']).total_seconds() / 3600
        if delta > max_gap:
            max_gap   = delta
            gap_start = df2.loc[i-1, 'date']
            gap_end   = df2.loc[i,   'date']
    return round(max_gap, 1), gap_start, gap_end


# ── STREAKS ───────────────────────────────────────────────────────────────────
def conversation_streaks(selected_user, df):
    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    active_days = sorted(pd.to_datetime(df['only_date'].unique()))
    if not active_days:
        return 0, 0, []

    max_streak = curr_streak_len = 1
    streaks = []
    for i in range(1, len(active_days)):
        if (active_days[i] - active_days[i-1]).days == 1:
            curr_streak_len += 1
            max_streak = max(max_streak, curr_streak_len)
        else:
            streaks.append(curr_streak_len)
            curr_streak_len = 1
    streaks.append(curr_streak_len)

    today   = pd.Timestamp.now().normalize()
    current = 0
    for day in reversed(active_days):
        if day == today - pd.Timedelta(days=current):
            current += 1
        else:
            break

    return max_streak, current, streaks


# ── LANGUAGE DETECTION ────────────────────────────────────────────────────────
def language_distribution(selected_user, df):
    if not LANGDETECT_OK:
        return pd.DataFrame({'language': ['langdetect not installed'], 'count': [0]})

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df2 = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()

    def safe_detect(text):
        try:
            if len(str(text).strip()) < 10:
                return 'unknown'
            return lang_detect(str(text))
        except Exception:
            return 'unknown'

    df2['language'] = df2['message'].apply(safe_detect)
    result = df2['language'].value_counts().reset_index()
    result.columns = ['language', 'count']
    return result


# ── TOPIC MODELING ────────────────────────────────────────────────────────────
def topic_modeling(selected_user, df, num_topics=5):
    try:
        from gensim import corpora
        from gensim.models import LdaModel
        from gensim.parsing.preprocessing import STOPWORDS
    except ImportError:
        return None, "gensim not installed. Run: pip install gensim"

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    df2 = df[
        (df['user'] != 'group_notification') &
        (df['message'] != '<Media omitted>')
    ].copy()

    stop_words = _load_stop_words()
    all_stops  = STOPWORDS.union(stop_words)

    def tokenize(text):
        return [w for w in str(text).lower().split()
                if w not in all_stops and len(w) > 3]

    texts = [tokenize(m) for m in df2['message']]
    texts = [t for t in texts if t]

    if len(texts) < 10:
        return None, "Not enough messages for topic modeling (need at least 10)."

    dictionary = corpora.Dictionary(texts)
    dictionary.filter_extremes(no_below=2, no_above=0.9)
    corpus = [dictionary.doc2bow(t) for t in texts]

    lda    = LdaModel(corpus=corpus, id2word=dictionary,
                      num_topics=num_topics, random_state=42, passes=10)
    topics = [
        {'topic': f'Topic {i+1}',
         'keywords': ', '.join(w for w, _ in lda.show_topics(formatted=False, num_words=8)[i][1])}
        for i in range(num_topics)
    ]
    return pd.DataFrame(topics), None


# ── PDF REPORT ────────────────────────────────────────────────────────────────
def _save_fig(fig):
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    fig.savefig(tmp.name, bbox_inches='tight', dpi=150)
    plt.close(fig)
    return tmp.name

def generate_pdf_report(selected_user, df):
    if not FPDF_OK:
        raise ImportError("fpdf2 not installed. Run: pip install fpdf2")

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Title ─────────────────────────────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 20)
    pdf.cell(0, 12, 'WhatsApp Chat Analysis Report', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.set_font('Helvetica', '', 12)
    pdf.cell(0, 8,  f'User: {selected_user}', new_x='LMARGIN', new_y='NEXT', align='C')
    pdf.ln(6)

    # ── Key stats ─────────────────────────────────────────────────────────────
    num_msg, num_word, num_media, num_links = fetch_stats(selected_user, df)
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Key Statistics', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    for label, val in [('Total Messages', num_msg), ('Total Words', num_word),
                        ('Media Shared',   num_media), ('Links Shared', num_links)]:
        pdf.cell(0, 8, f'  {label}: {val}', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # ── Sentiment summary ─────────────────────────────────────────────────────
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'Sentiment Summary', new_x='LMARGIN', new_y='NEXT')
    pdf.set_font('Helvetica', '', 12)
    counts = sentiment_counts(selected_user, df)
    for sentiment, count in counts.items():
        pdf.cell(0, 8, f'  {sentiment}: {count} messages', new_x='LMARGIN', new_y='NEXT')
    pdf.ln(4)

    # ── Monthly timeline chart ────────────────────────────────────────────────
    timeline = monthly_timeline(selected_user, df)
    if not timeline.empty:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(timeline['time'], timeline['message'], marker='o')
        ax.set_title('Monthly Timeline')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = _save_fig(fig)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Monthly Timeline', new_x='LMARGIN', new_y='NEXT')
        pdf.image(path, w=180)
        os.unlink(path)
        pdf.ln(4)

    # ── Sentiment trend chart ─────────────────────────────────────────────────
    trend = daily_sentiment_trend(selected_user, df)
    if not trend.empty:
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(trend['date'], trend['rolling_avg'], color='green')
        ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
        ax.set_title('Sentiment Trend (7-day rolling avg)')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = _save_fig(fig)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Sentiment Trend', new_x='LMARGIN', new_y='NEXT')
        pdf.image(path, w=180)
        os.unlink(path)
        pdf.ln(4)

    # ── Most active users (overall only) ─────────────────────────────────────
    if selected_user == 'Overall':
        x, _ = most_busy_users(df)
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.bar(x.index, x.values)
        ax.set_title('Most Active Users')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        path = _save_fig(fig)
        pdf.set_font('Helvetica', 'B', 14)
        pdf.cell(0, 10, 'Most Active Users', new_x='LMARGIN', new_y='NEXT')
        pdf.image(path, w=180)
        os.unlink(path)

    return bytes(pdf.output())