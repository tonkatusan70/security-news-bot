import requests
import google.generativeai as genai
import tweepy
import os

# --- 環境変数からAPIキーを取得 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# --- Google Gemini API セットアップ ---
genai.configure(api_key=GEMINI_API_KEY)

# --- X API 認証 ---
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)

# --- Google News RSS からニュースを取得 ---
def get_security_news():
    """Google News RSSを使って最新のサイバーセキュリティニュースを取得"""
    rss_url = "https://news.google.com/rss/search?q=サイバーセキュリティ&hl=ja&gl=JP&ceid=JP:ja"
    response = requests.get(rss_url)
    
    if response.status_code != 200:
        return "ニュースを取得できませんでした。"

    from xml.etree import ElementTree as ET
    root = ET.fromstring(response.content)
    items = root.findall(".//item")

    news_list = []
    for item in items[:3]:  # 最新3件を取得
        title = item.find("title").text
        link = item.find("link").text
        news_list.append(f"{title}\n{link}")

    return "\n\n".join(news_list)

# --- Google Gemini APIで要約 ---
def summarize_news(news_text):
    """ニュース記事の要約を生成"""
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(f"以下のニュースを簡潔に要約してください:\n\n{news_text}")
    return response.text.strip()

# --- X に投稿 ---
def post_to_x():
    """ニュースを要約してXに投稿"""
    news_text = get_security_news()
    summary = summarize_news(news_text)
    
    tweet = f"【最新のセキュリティニュース】\n{summary}"
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    api.update_status(tweet)
    print("投稿完了:", tweet)

# --- メイン処理 ---
if __name__ == "__main__":
    post_to_x()
