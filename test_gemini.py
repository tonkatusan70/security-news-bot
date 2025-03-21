import google.generativeai as genai
import os

# 環境変数からAPIキーを取得
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Google Gemini API 設定
genai.configure(api_key=GEMINI_API_KEY)

# 利用可能なモデルをリストアップ
models = genai.list_models()

# モデル一覧を表示
print("\n利用可能なモデル一覧:")
for model in models:
    print("-", model.name)
