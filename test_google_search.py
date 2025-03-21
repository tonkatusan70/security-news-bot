import os
import requests

# 環境変数から API キーと検索エンジン ID (CX) を取得
API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")  # Secrets に設定した API キー名
CX = os.getenv("GOOGLE_SEARCH_CX")  # Secrets に設定した検索エンジン ID 名

# Google Search API のエンドポイント
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# 検索キーワード（最新のサイバーセキュリティニュース）
QUERY = "latest cybersecurity news"

def search_google():
    """Google Search API を使ってニュースを取得し、タイトルと URL を表示する"""
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": QUERY,
        "num": 5,  # 上位5件の結果を取得
    }

    response = requests.get(SEARCH_URL, params=params)
    
    if response.status_code == 200:
        results = response.json().get("items", [])
        if results:
            print("\n🔹 最新のセキュリティニュース:")
            for i, result in enumerate(results):
                print(f"{i+1}. {result['title']} - {result['link']}")
        else:
            print("⚠️ ニュースが見つかりませんでした。")
    else:
        print(f"❌ エラー発生: {response.status_code}")
        print("詳細:", response.json())

if __name__ == "__main__":
    if API_KEY and CX:
        search_google()
    else:
        print("❌ APIキーまたはCXが設定されていません。")
