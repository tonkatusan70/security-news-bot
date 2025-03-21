import os
import google.generativeai as genai
import requests
import tweepy

# --- API キーの設定 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# --- Google Gemini API 設定 ---
genai.configure(api_key=GEMINI_API_KEY)

# 最新の利用可能なモデル
MODEL_NAME = "models/gemini-1.5-pro-latest"

# --- X API 認証 ---
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


# --- ニュース取得 ---
def get_security_news():
    """最新のセキュリティニュースを取得"""
    url = "https://newsapi.org/v2/top-headlines"
    params = {
        "q": "サイバーセキュリティ",
        "language": "ja",
        "apiKey": os.getenv("NEWS_API_KEY")  # NewsAPIのキー
    }
    
    response = requests.get(url, params=params)
    articles = response.json().get("articles", [])

    if not articles:
        return None
    
    # ニュース記事のタイトルとURLを取得
    news_text = ""
    for article in articles[:3]:  # 最新3件のみ
        title = article["title"]
        url = article["url"]
        news_text += f"{title}\n{url}\n\n"
    
    return news_text.strip()


# --- ニュース要約 ---
def summarize_news(news_text):
    """Geminiを使ってニュースを要約"""
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(f"以下のニュースを簡潔に要約してください:\n\n{news_text}")
        return response.text.strip()
    except Exception as e:
        print("要約中にエラーが発生しました:", str(e))
        return None


# --- X に投稿 ---
def post_to_x():
    """ニュースを要約し、X に投稿"""
    news_text = get_security_news()
    if not news_text:
        print("最新のニュースが見つかりませんでした。")
        return

    summary = summarize_news(news_text)
    if not summary:
        print("要約に失敗しました。投稿をスキップします。")
        return

    post_text = f"【最新のセキュリティニュース】\n{summary[:250]}"  # 280文字制限
    try:
        api.update_status(post_text)
        print("投稿完了:", post_text)
    except Exception as e:
        print("X 投稿中にエラーが発生しました:", str(e))


# --- メイン処理 ---
if __name__ == "__main__":
    post_to_x()
