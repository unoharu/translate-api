from fastapi import FastAPI
import requests

app = FastAPI()

url = "http://localhost:8000/translate" 

data = {
    "text": "Hello, World!",
    "target_lang": "ja"
}

response = requests.post(url, json=data)

# レスポンスの内容を表示
print(response.json())

# ステータスコードを取得
status_code = response.status_code
print("status : " + str(status_code))