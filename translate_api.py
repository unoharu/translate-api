from fastapi import FastAPI
import requests

app = FastAPI()

# 対応する言語リスト
supported_languages = ['en', 'ja']

def create_error_response(status_code: int, detail: str):
    error_response = {"status": f"error:{status_code}", "message": detail}
    print(error_response)
    return error_response, status_code

# 自作のAPIのエンドポイント
@app.post("/translate")
async def translate(data: dict):
    target_lang = data.get("target_lang")
    text = data.get("text")

    if target_lang == "ja":
        lang = "日本語"
    elif target_lang == "en":
        lang = "英語"

    request_text = f'''
    以下のテキストを{lang}に翻訳してください。
    ただし、メンションやメールアドレスと想定されるものは翻訳しないでください。

    {text}
    '''

    # モックAPIのURL（モックAPIにリクエストを転送）
    mock_api_url = "http://localhost:8001/v1/chat/completions"

    try:
        # モックAPIに転送するデータを整形
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": request_text}
            ]
        }

        # モックAPIにPOSTリクエストを送信
        response = requests.post(mock_api_url, json=payload)

        # モックAPIからのレスポンスを取得
        response_data = response.json()

        # レスポンスが成功した場合の処理
        if response.status_code == 200:
            translated_text = response_data["choices"][0]["message"]["content"]
            return {"status": "success", "translated_text": translated_text}
        
    except Exception as e:
        # その他の例外発生時のエラーハンドリング
        return create_error_response(500, "予期しないエラーが発生しました。")
