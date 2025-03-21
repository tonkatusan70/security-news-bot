import os
import requests
import google.generativeai as genai
import tweepy

# ✅ 環境変数から API キーを取得
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")
X_API_SECRET = os.getenv("X_API_SECRET")
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")

# ✅ API の設定
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
QUERY = "latest cybersecurity news"
POST_LIMIT = 3  # 1回の実行で投稿するニュース数

# ✅ Google Gemini API の設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ✅ Twitter API の認証
auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)


def search_google():
    """Google Search API を使って最新のニュースを取得"""
    if not GOOGLE_SEARCH_API_KEY or not GOOGLE_SEARCH_CX:
        print("❌ APIキーまたは検索エンジンIDが設定されていません。")
        return []

    params = {
        "key": GOOGLE_SEARCH_API_KEY,
        "cx": GOOGLE_SEARCH_CX,
        "q": QUERY,
        "num": POST_LIMIT,
        "lr": "lang_ja",  # 日本語のニュースを取得
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


def summarize_news(title, description):
    """Gemini API を使ってニュース記事を要約（タイトルを日本語化し、内容を簡潔にする）"""
    prompt = f"""
    以下のニュースのタイトルを日本語に翻訳し、本文をわかりやすく要約してください。
    タイトル: {title}
    本文: {description}
    
    出力形式:
    【タイトル（日本語訳）】
    要約（140文字以内）
    """

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"❌ 要約中にエラーが発生しました: {e}")
        return None


def post_to_x():
    """最新のニュースを取得し、要約して X に投稿"""
    news_items = search_google()
    if not news_items:
        print("⚠️ 最新のニュースが見つかりませんでした。")
        return

    for news in news_items:
        title = news["title"]
        description = news.get("snippet", "")
        link = news["link"]

        summary = summarize_news(title, description)

        if summary:
            # ✅ 投稿用のフォーマット
            tweet_content = f"{summary}\n{link}"

            # ✅ 文字数制限を考慮（280文字以内）
            if len(tweet_content) > 280:
                tweet_content = f"{summary[:250]}…\n{link}"

            try:
                api.update_status(tweet_content)
                print(f"✅ 投稿成功: {tweet_content}")
            except Exception as e:
                print(f"❌ X への投稿に失敗しました: {e}")
        else:
            print("⚠️ 要約に失敗したため投稿をスキップ")


if __name__ == "__main__":
    post_to_x()
