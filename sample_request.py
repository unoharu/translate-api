import requests

url = "http://localhost:8000/translate"  # 正しいエンドポイント

data = {
    "text": "Hello, World! ja"  # 言語コードを含むテキスト
}

response = requests.post(url, data=data)  # フォームデータとして送信

print(response.status_code)
print(response.text)  # プレーンテキストとしてレスポンスを表示