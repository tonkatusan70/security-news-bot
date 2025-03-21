import os
import requests

# 環境変数から API キーと検索エンジン ID を取得
API_KEY = os.getenv("GOOGLE_SEARCH_API_KEY")
CX = os.getenv("GOOGLE_SEARCH_CX")

# Google Search API のエンドポイント
SEARCH_URL = "https://www.googleapis.com/customsearch/v1"

# 検索キーワード
QUERY = "latest cybersecurity news"

def search_google():
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": QUERY
    }

    response = requests.get(SEARCH_URL, params=params)
    if response.status_code == 200:
        results = response.json().get("items", [])
        for i, result in enumerate(results[:5]):
            print(f"{i+1}. {result['title']} - {result['link']}")
    else:
        print("Error:", response.json())

if __name__ == "__main__":
    if API_KEY and CX:
        search_google()
    else:
        print("APIキーまたはCXが設定されていません。")
