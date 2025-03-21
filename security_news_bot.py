import requests
import google.generativeai as genai
import xml.etree.ElementTree as ET
import os

# --- 環境変数からAPIキーを取得 ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# --- Google Gemini API セットアップ ---
genai.configure(api_key=GEMINI_API_KEY)

def summarize_news(news_text):
    """ニュース記事の要約を生成"""
    try:
        model = genai.GenerativeModel('gemini-pro')  # 修正: 最新バージョンならこれでOK
        response = model.generate_content(f"以下のニュースを簡潔に要約してください:\n\n{news_text}")
        return response.text.strip()
    except Exception as e:
        return f"要約中にエラーが発生しました: {e}"

# --- Google News RSS からニュースを取得 ---
def get_security_news():
    """Google News RSSを使って最新のサイバーセキュリティニュースを取得"""
    rss_url = "https://news.google.com/rss/search?q=サイバーセキュリティ&hl=ja&gl=JP&ceid=JP:ja"
    
    try:
        response = requests.get(rss_url, timeout=10)
        if response.status_code != 200:
            return "ニュースを取得できませんでした。"

        root = ET.fromstring(response.content)
        items = root.findall(".//item")

        news_list = []
        for item in items[:3]:  # 最新3件を取得
            title = item.find("title").text
            link = item.find("link").text
            news_list.append(f"{title}\n{link}")

        return "\n\n".join(news_list)
    except Exception as e:
        return f"ニュース取得中にエラーが発生しました: {e}"

# --- 実行処理 ---
if __name__ == "__main__":
    news_text = get_security_news()
    summary = summarize_news(news_text)
    print("取得したニュース:\n", news_text)
    print("\n要約:\n", summary)
