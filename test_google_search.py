import requests
import os

# 環境変数からAPIキーとカスタム検索エンジンIDを取得
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

# 検索クエリの設定（例: サイバーセキュリティ ニュース）
query = "サイバーセキュリティ ニュース"
url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&key={GOOGLE_API_KEY}"

# APIリクエストを送信
response = requests.get(url)

# 結果の表示
if response.status_code == 200:
    data = response.json()
    print("\n🔎 検索結果一覧:")
    for item in data.get("items", []):
        print(f"- {item['title']}: {item['link']}")
else:
    print("⚠️ エラー:", response.json())
