import os
import requests
import google.generativeai as genai
import tweepy

# ✅ 環境変数から API キーを取得
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")  # Google Search API Key
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")  # Custom Search Engine ID
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Gemini API Key
X_API_KEY = os.getenv("X_API_KEY")  # Twitter API Key
X_API_SECRET = os.getenv("X_API_SECRET")  # Twitter API Secret
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")  # Twitter Access Token
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")  # Twitter Access Token Secret

# ✅ Google Search API のエンドポイント
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
QUERY = "latest cybersecurity news"

# ✅ Google Gemini API の設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ✅ Twitter API の認証
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def search_google():
    """Google Search API を使って最新のニュースを取得する"""
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        print("❌ APIキーまたは検索エンジンIDが設定されていません。")
        return []

    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_SEARCH_CX,
        "q": QUERY,
        "num": 3,  # 3件のニュースを取得
        "lr": "lang_en",
        "sort": "date"
    }

    try:
        response = requests.get(SEARCH_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTPリクエストエラー: {e}")
        return []


def summarize_news(news_text):
    """Gemini API を使ってニュース記事を要約する"""
    try:
        response = model.generate_content(f"以下のニュースを100文字以内で要約してください:\n\n{news_text}")
        return response.text.strip()
    except Exception as e:
        print(f"❌ 要約中にエラーが発生しました: {e}")
        return None


def post_to_x():
    """最新のニュースを取得し、要約して X に投稿する"""
    news_items = search_google()
    if not news_items:
        print("⚠️ 最新のニュースが見つかりませんでした。")
        return

    for news in news_items:
        title = news["title"]
        link = news["link"]
        summary = summarize_news(title)

        if summary:
            # ✅ 投稿用のフォーマット
            tweet_content = f"📰 {title}\n\n🔹 {summary}\n🔗 {link}"
            
            # ✅ 文字数制限を考慮（X は最大 280 文字）
            if len(tweet_content) > 280:
                tweet_content = f"📰 {title}\n🔗 {link}"  # 長すぎる場合はタイトルとURLのみ

            try:
                api.update_status(tweet_content)
                print(f"✅ 投稿成功: {tweet_content}")
            except Exception as e:
                print(f"❌ X への投稿に失敗しました: {e}")
        else:
            print("⚠️ 要約に失敗したため投稿をスキップ")


if __name__ == "__main__":
    post_to_x()
