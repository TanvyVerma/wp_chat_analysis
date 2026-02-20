import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns

# PAGE CONFIG
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide"
)

# SIDEBAR 
st.sidebar.markdown("## 💬 WhatsApp Chat Analyzer")
st.sidebar.markdown("Upload your chat file and explore insights 📊")

uploaded_file = st.sidebar.file_uploader("📂 Upload chat file")

# MAIN APP 
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode('utf-8')
    df = preprocessor.preprocess(data)

    # USER SELECTION
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')

    user_list.sort()
    user_list.insert(0, 'Overall')

    st.sidebar.markdown("---")
    selected_user = st.sidebar.selectbox(
        "👤 Select User",
        user_list
    )

    if st.sidebar.button("🚀 Show Analysis"):

        # HEADER 
        st.markdown(
            f"<h1 style='text-align:center;'>📊 Chat Analysis</h1>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<h3 style='text-align:center;color:gray;'>User: {selected_user}</h3>",
            unsafe_allow_html=True
        )

        st.markdown("---")

        # TOP STATISTICS
        num_msg, num_word, num_media, num_links = helper.fetch_stats(selected_user, df)

        st.markdown("## 🔢 Key Statistics")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("💬 Messages", num_msg)

        with col2:
            st.metric("📝 Words", num_word)

        with col3:
            st.metric("📸 Media", num_media)

        with col4:
            st.metric("🔗 Links", num_links)

        st.markdown("---")

        # TIMELINES
        st.markdown("## ⏳ Message Timeline")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📆 Monthly Timeline")
            timeline = helper.monthly_timeline(selected_user, df)
            if timeline is not None and not timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(timeline['time'], timeline['message'])
                plt.xticks(rotation=90)
                st.pyplot(fig)
            else:
                st.info("No monthly data available")

        with col2:
            st.markdown("### 🗓 Daily Timeline")
            daily_timeline = helper.daily_timeline(selected_user, df)
            if daily_timeline is not None and not daily_timeline.empty:
                fig, ax = plt.subplots()
                ax.plot(daily_timeline['only_date'], daily_timeline['message'])
                plt.xticks(rotation=90)
                st.pyplot(fig)
            else:
                st.info("No daily data available")

        st.markdown("---")

        # ACTIVITY MAP
        st.markdown("## 📌 Activity Overview")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 📅 Most Active Days")
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        with col2:
            st.markdown("### 🗓 Most Active Months")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values)
            plt.xticks(rotation=45)
            st.pyplot(fig)

        st.markdown("---")

        # HEATMAP
        st.markdown("## 🔥 Weekly Activity Heatmap")
        user_heatmap = helper.activity_heatmap(selected_user, df)

        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        st.pyplot(fig)

        st.markdown("---")

        # MOST BUSY USERS
        if selected_user == 'Overall':
            st.markdown("## 🏆 Most Active Users")
            x, new_df = helper.most_busy_users(df)

            col1, col2 = st.columns(2)

            with col1:
                fig, ax = plt.subplots()
                ax.bar(x.index, x.values)
                plt.xticks(rotation=45)
                st.pyplot(fig)

            with col2:
                st.dataframe(new_df, use_container_width=True)

            st.markdown("---")

        # WORDCLOUD
        st.markdown("## ☁️ Word Cloud")
        df_wc = helper.create_wordcloud(selected_user, df)
        fig, ax = plt.subplots()
        ax.imshow(df_wc)
        ax.axis("off")
        st.pyplot(fig)

        st.markdown("---")

        # COMMON WORDS
        st.markdown("## 🔠 Most Common Words")
        most_common_df = helper.most_common_words(selected_user, df)
        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        st.pyplot(fig)

        st.markdown("---")

        # EMOJI ANALYSIS
        st.markdown("## 😄 Emoji Analysis")
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2 = st.columns(2)

        with col1:
            st.dataframe(emoji_df, use_container_width=True)

        with col2:
            fig, ax = plt.subplots()
            ax.pie(
                emoji_df[1].head(),
                labels=emoji_df[0].head(),
                autopct="%0.2f"
            )
            st.pyplot(fig)
















