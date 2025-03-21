import requests
import google.generativeai as genai
import tweepy
import os
import xml.etree.ElementTree as ET

# --- 環境変数からAPIキーを取得 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# --- Google Gemini API セットアップ ---
genai.configure(api_key=GEMINI_API_KEY)

def summarize_news(news_text):
    """ニュース記事の要約を生成"""
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(f"以下のニュースを簡潔に要約してください:\n\n{news_text}")
        return response.text.strip()
    except Exception as e:
        print("要約中にエラーが発生しました:", e)
        return None

# --- Google News RSS からニュースを取得 ---
def get_security_news():
    """Google News RSSを使って最新のサイバーセキュリティニュースを取得"""
    rss_url = "https://news.google.com/rss/search?q=サイバーセキュリティ&hl=ja&gl=JP&ceid=JP:ja"
    
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code != 200:
            print("ニュースを取得できませんでした。")
            return None

        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        news_list = []
        for item in items[:3]:  # 最新3件を取得
            title = item.find("title").text
            link = item.find("link").text
            news_list.append(f"{title}\n{link}")

        return "\n\n".join(news_list)
    except Exception as e:
        print("ニュース取得中にエラーが発生しました:", e)
        return None

# --- X に投稿 ---
def post_to_x():
    """ニュースを要約してXに投稿"""
    news_text = get_security_news()
    if not news_text:
        print("ニュース取得に失敗しました。投稿をスキップします。")
        return
    
    summary = summarize_news(news_text)
    if not summary:
        print("要約に失敗しました。投稿をスキップします。")
        return
    
    tweet = f"【最新のセキュリティニュース】\n{summary}"
    if len(tweet) > 280:
        tweet = tweet[:277] + "..."
    
    try:
        auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
        auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
        api = tweepy.API(auth)

        # 投稿テスト (デバッグ用)
        print("投稿内容:", tweet)
        
        api.update_status(tweet)
        print("✅ Xへの投稿完了！")
    except Exception as e:
        print("❌ Xへの投稿中にエラーが発生しました:", e)

# --- メイン処理 ---
if __name__ == "__main__":
    post_to_x()
