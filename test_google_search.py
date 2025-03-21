import os
import requests

# ✅ 環境変数から API キーと検索エンジン ID を取得
API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")  # GitHub Secrets で登録したAPIキー
CX = os.getenv("GOOGLE_SEARCH_CX")  # GitHub Secrets で登録した検索エンジンID

# ✅ Google Search API のエンドポイント
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# ✅ 検索キーワード
QUERY = "latest cybersecurity news"  # 英語のほうがヒットしやすい

def search_google():
    """Google Search API を使ってニュースを取得する"""

    if not API_KEY or not CX:
        print("❌ APIキーまたは検索エンジンID (CX) が設定されていません。")
        return

    params = {
        "key": API_KEY,
        "cx": CX,
        "q": QUERY,
        "num": 5,  # ✅ 5件のニュースを取得
        "lr": "lang_en",  # ✅ 英語のニュースのみを取得（日本語なら lang_ja）
        "sort": "date"  # ✅ 最新ニュース順にソート
    }

    try:
        response = requests.get(SEARCH_URL, params=params)
        response.raise_for_status()  # 4xx, 5xx エラーがあれば例外発生

        data = response.json()
        results = data.get("items", [])

        if results:
            print("\n🔹 最新のセキュリティニュース:")
            for i, result in enumerate(results, start=1):
                print(f"{i}. {result['title']} - {result['link']}")
        else:
            print("⚠️ ニュースが見つかりませんでした。")

    except requests.exceptions.RequestException as e:
        print(f"❌ HTTPリクエストエラー: {e}")

if __name__ == "__main__":
    search_google()
