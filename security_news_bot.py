import os
import requests
import google.generativeai as genai
import tweepy
import time
import argparse
from datetime import datetime

# ✅ 環境変数から API キーを取得
GOOGLE_SEARCH_API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")  # Google Search API Key
GOOGLE_SEARCH_CX = os.getenv("GOOGLE_SEARCH_CX")  # Custom Search Engine ID
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Gemini API Key
X_API_KEY = os.getenv("X_API_KEY")  # X API Key
X_API_SECRET = os.getenv("X_API_SECRET")  # X API Secret
X_ACCESS_TOKEN = os.getenv("X_ACCESS_TOKEN")  # X Access Token
X_ACCESS_TOKEN_SECRET = os.getenv("X_ACCESS_TOKEN_SECRET")  # X Access Token Secret

# ✅ Google Search API のエンドポイント
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"
QUERY = "latest cybersecurity news"

# ✅ Google Gemini API の設定
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# ✅ X API の認証
client = tweepy.Client(
    consumer_key=X_API_KEY,
    consumer_secret=X_API_SECRET,
    access_token=X_ACCESS_TOKEN,
    access_token_secret=X_ACCESS_TOKEN_SECRET
)

# ✅ 投稿する時間（JST基準）
POST_TIMES = ["07:00", "12:00", "20:00"]


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

        if "items" not in data:
            print("⚠️ 検索結果が見つかりませんでした。")
            return []

        return data["items"]

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTPリクエストエラー: {e}")
        return []


def translate_to_japanese(text):
    """英語のニュースタイトルを日本語に翻訳"""
    try:
        response = model.generate_content(f"以下の英語のニュースタイトルを自然な日本語に翻訳してください:\n\n{text}")
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print(f"❌ 翻訳中にエラーが発生しました: {e}")
        return text  # 失敗した場合はそのまま英語を返す


def summarize_news(news_text):
    """Gemini API を使ってニュース記事を要約する"""
    try:
        response = model.generate_content(f"以下のニュースを100文字以内で簡潔に要約してください:\n\n{news_text}")
        return response.candidates[0].content.parts[0].text.strip()
    except Exception as e:
        print(f"❌ 要約中にエラーが発生しました: {e}")
        return None


def should_post_now():
    """現在時刻が指定された投稿時間に一致するかを確認"""
    now = datetime.now().strftime("%H:%M")
    return now in POST_TIMES


def post_to_x(force_post=False):
    """最新のニュースを取得し、要約して X に投稿する"""
    if not force_post and not should_post_now():
        print("⏳ 現在は投稿時間ではありません。")
        return

    news_items = search_google()
    if not news_items:
        print("⚠️ 最新のニュースが見つかりませんでした。")
        return

    # ✅ 強制投稿時は1件のみ投稿
    if force_post:
        news_items = news_items[:1]

    for news in news_items:
        title_en = news["title"]
        link = news["link"]
        title_jp = translate_to_japanese(title_en)  # 日本語に翻訳
        summary = summarize_news(title_jp)

        if summary:
            # ✅ 投稿用のフォーマット
            tweet_content = f"【{title_jp}】\n\n{summary}\n{link}"
            
            # ✅ 文字数制限を考慮（X は最大 280 文字）
            if len(tweet_content) > 280:
                tweet_content = f"【{title_jp}】\n{link}"  # 長すぎる場合はタイトルとURLのみ
            
            print(f"📢 投稿内容: {tweet_content}")  # 投稿前に内容をログ出力

            # ✅ 投稿試行（最大3回）
            for attempt in range(3):
                try:
                    response = client.create_tweet(text=tweet_content)
                    print(f"✅ 投稿成功: {tweet_content}\n🔹 Tweet ID: {response.data['id']}")
                    break  # 成功したらループを抜ける
                except tweepy.TweepError as e:
                    print(f"❌ X への投稿に失敗しました（試行 {attempt+1}/3 回目）: {e}")
                    if attempt < 2:  # 最後の試行でなければ待機
                        print("🔄 5秒待機して再試行...")
                        time.sleep(5)
                    else:
                        print("⚠️ 投稿に3回失敗したためスキップ")
        else:
            print("⚠️ 要約に失敗したため投稿をスキップ")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ニュースを X に投稿")
    parser.add_argument("--test", action="store_true", help="テスト投稿（1回のみ投稿）")
    args = parser.parse_args()

    post_to_x(force_post=args.test)
