<!-- # WhatsApp Chat Analysis 📊💬

WhatsApp Chat Analysis is a web application that allows users to upload exported WhatsApp chat files and get meaningful insights, statistics, and visualizations from conversations.

The project analyzes chat data such as total messages, active users, most used words, emojis, media count, timelines, and activity patterns.

---

## 🚀 Features

* Upload exported WhatsApp `.txt` chat file
* Total messages count
* Total words used
* Media messages count
* Shared links count
* Most active users (for group chats)
* Most common words used
* Emoji analysis
* Daily / Monthly timeline charts
* Weekly activity heatmap
* User-wise message comparison
* Clean and interactive dashboard

---

## 🛠️ Tech Stack

### Frontend

* HTML
* CSS
* JavaScript
  or
* React.js (advanced version)

### Backend

* Python

### Libraries / Tools

* Streamlit / Flask
* Pandas
* Matplotlib
* Seaborn
* Emoji
* Regex

---

## 📁 Project Structure

whatsapp-chat-analysis/
│── app.py
│── helper.py
│── preprocessor.py
│── requirements.txt
│── README.md

(If React version)

whatsapp-chat-analysis/
│── client/
│── server/

---

## ▶️ How to Run the Project

### Step 1: Clone Repository

git clone <your-repo-link>

### Step 2: Open Project Folder

cd whatsapp-chat-analysis

### Step 3: Install Dependencies

pip install -r requirements.txt

### Step 4: Run Project

streamlit run app.py

### Step 5: Open Browser

The app will open automatically in browser.

---

## 📤 How to Use

### Export WhatsApp Chat

1. Open WhatsApp chat
2. Click More Options
3. Export Chat
4. Choose **Without Media**
5. Save `.txt` file

### Upload in App

* Open project
* Upload exported chat file
* Select user (optional)
* View analytics dashboard

---

## 📊 Insights Provided

### General Stats

* Total Messages
* Total Words
* Media Shared
* Links Shared

### Timeline Analysis

* Monthly timeline
* Daily timeline
* Most active dates

### User Analysis

* Most active members
* Individual contribution %

### Content Analysis

* Common words
* Emoji usage
* Most used emojis

### Activity Analysis

* Most active day
* Most active month
* Heatmap of active hours

---

## 🧠 Learning Outcomes

This project helps understand:

* Text preprocessing
* Data cleaning
* Regex parsing
* Data visualization
* Dashboard building
* Python data analysis
* Real-world dataset handling

---

## 🔮 Future Improvements

* Sentiment analysis
* AI relationship insights
* Toxicity detection
* Mood trend graph
* Chat summarizer
* React frontend version
* User authentication
* PDF report export

---

## 📸 Use Cases

* Analyze personal chats
* Group activity insights
* Fun statistics
* Learning NLP basics
* Portfolio project

---

## 🙌 Author

Built by **Tanvy Verma** as a learning project for chat analytics and data visualization.

---

## ⭐ If You Like This Project

Give it a star on GitHub and keep building amazing projects 🚀 -->



















# 💬 ChatLens · WhatsApp Analytics Dashboard

A production-grade WhatsApp chat analytics dashboard built with Python and Streamlit.
Upload any WhatsApp `.txt` export and get instant, insight-driven analytics with
interactive Plotly charts, sentiment analysis, topic modeling, and PDF export.

---

## ✨ Features

| Category | What you get |
|---|---|
| **Parsing** | Android & iOS formats · 12h & 24h clocks · multiline messages · system messages |
| **Overview** | Bento stat grid · activity heatmap (correctly ordered) · busy users · chat-summary hero |
| **New metrics** | Conversation starters · reply ratio · silent days · peak hour slot |
| **Sentiment** | Donut chart · daily trend (7-day rolling) · per-user ranking |
| **Response time** | Per-user avg · distribution histogram · hourly pattern · longest silence |
| **Timelines** | Monthly & daily interactive charts · streak tracker |
| **Deep analysis** | Word cloud (theme-aware) · top-20 words · top keywords per user · emoji donut · language detection · LDA topic modeling |
| **Export** | PDF report with charts, stats, starters, and sentiment (button-gated, no auto-run) |
| **UI** | True-black `#080B12` + glassmorphism cards · Plotly throughout · Clash Display headings · DM Mono metrics · insight captions on every chart |

---

## 🗂️ File Structure

```
chatlens/
├── app.py              ← Main Streamlit application (rewritten)
├── helper.py           ← All analytics functions (rewritten + 4 new functions)
├── preprocessor.py     ← Robust multi-format WhatsApp parser (rewritten)
├── stop_hinglish.txt   ← Hinglish stop-word list (keep in same folder)
├── requirements.txt    ← All Python dependencies
└── README.md           ← This file
```

---

## 🚀 Quick Start

### 1. Clone / download the project

```bash
git clone <your-repo-url>
cd chatlens
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `gensim` (for topic modeling) can be slow to install.
> If you don't need topic modeling, comment it out in `requirements.txt`.

### 4. Run the app

```bash
streamlit run app.py
```

---

## 📱 How to Export a WhatsApp Chat

**Android:**
Open chat → ⋮ Menu → More → Export chat → Without media → Save the `.txt` file

**iPhone:**
Open chat → Contact name → Export Chat → Without Media → Save the `.txt` file

---

## 🧠 Key Improvements Over Original

### Bugs Fixed
| Bug | Fix |
|---|---|
| Stop-words loaded as raw string (substring match) | Now loaded as a `set` — correct word-boundary matching |
| Android 12-hour format silently skipped | Regex extended to match `2:05 pm` style |
| Multiline messages split as phantom entries | `re.MULTILINE` split on line-start headers only |
| Word count included `<Media omitted>` words | Media and deleted stubs excluded before counting |
| `stop_hinglish.txt` path broke on Streamlit Cloud | Now resolved via `__file__`-relative path with cwd fallback |
| PDF generated on every Streamlit re-run | Gated behind an explicit button click |
| Heatmap day order was alphabetical / random | Reindexed to Mon–Sun before rendering |
| Pie charts broke with < 2 emojis | Bar chart fallback added |

### New Functions in `helper.py`
| Function | What it does |
|---|---|
| `conversation_starters(df)` | Who sends first after 60-min+ gaps |
| `reply_ratios(df)` | Reactive vs proactive score per user |
| `silent_days(user, df)` | Every calendar date with zero messages |
| `top_keywords_per_user(df)` | Per-user top words, stop-words removed |

### UI Upgrades
- **All Matplotlib charts replaced with Plotly** — hover tooltips, zoom, smooth animations
- **Glassmorphism cards** — `backdrop-filter: blur(16px)` + subtle borders
- **True-black background** `#080B12` — not a grey-black like before
- **Bento grid stat cards** — different accent colors, insight captions
- **Chat summary hero banner** — auto-generated 2-sentence overview at the top
- **Donut charts** — replace pie charts, center label shows the key percentage
- **Avatar chips** — colored initials circles next to every user name in tables
- **Insight boxes** — every major chart gets a plain-English interpretation
- **Clash Display** headings + **DM Mono** metric numbers with `font-feature-settings: "tnum"`

---

## ⚙️ Configuration

All visual design tokens live in `get_tokens()` near the top of `app.py`.
Change colors there — everything else updates automatically.

```python
def get_tokens(dark: bool) -> dict:
    if dark:
        return dict(
            bg      = "#080B12",   # ← change page background here
            accent  = "#0EA5E9",   # ← change primary accent color here
            ...
        )
```

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: wordcloud` | `pip install wordcloud` |
| `ModuleNotFoundError: fpdf` | `pip install fpdf2` (not `fpdf`) |
| Topic modeling missing | `pip install gensim` |
| Language detection missing | `pip install langdetect` |
| Word cloud shows wrong colors | Toggle dark/light mode — background is now theme-aware |
| Empty DataFrame after upload | Make sure the file is exported **without media** from WhatsApp |

---

## 📋 Dependencies

See `requirements.txt` for full pinned list. Core stack:

- **Streamlit** — web framework
- **Pandas / NumPy** — data processing
- **Plotly** — interactive charts
- **Matplotlib / Seaborn** — heatmap rendering
- **VADER** — sentiment analysis
- **WordCloud** — word cloud generation
- **fpdf2** — PDF export
- **URLExtract** — link detection
- **emoji** — emoji extraction
- **langdetect** — language detection (optional)
- **gensim** — LDA topic modeling (optional)