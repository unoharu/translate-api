from fastapi import FastAPI, HTTPException
import requests

app = FastAPI()

# 対応する言語リスト
supported_languages = ['en', 'ja']

def create_error_response(detail):
    return {"status": "error", "message": detail}

@app.post("/translate")
def translate_text(data: dict):
    target_lang = data.get("target_lang")
    text = data.get("text")

    # target_langが未入力の場合
    if not target_lang:
        return create_error_response(f"言語が指定されていません。{supported_languages} のいずれかを指定してください。")

    # 対応していない言語がリクエストされた場合
    if target_lang not in supported_languages:
        return create_error_response(f"{target_lang} は対応していない言語です。{supported_languages}のいずれかを指定してください。")

    # 翻訳するテキストが未入力の場合
    if not text:
        return create_error_response("textを入力してください。")

    # モックAPIのURL（モックAPIにリクエストを転送）
    mock_api_url = "http://localhost:8001/v1/chat/completions"

    try:
        # モックAPIに転送するデータを整形
        payload = {
            "model": "gpt-3.5-turbo",  # 使いたいモデル名
            "messages": [
                {"role": "user", "content": text}
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
        else:
            if response.status_code == 400:
                error_message = "外部APIに不正なリクエストが送信されました。"
            elif response.status_code == 404:
                error_message = "外部APIのエンドポイントが見つかりません。"
            elif response.status_code == 500:
                error_message = "外部APIで内部サーバーエラーが発生しました。"
            elif response.status_code == 502:
                error_message = "外部APIのゲートウェイエラーが発生しました。"
            elif response.status_code == 503:
                error_message = "外部APIが一時的に利用できません。"
            else:
                error_message = "外部APIでエラーが発生しました。"

            return create_error_response(error_message)

    except requests.exceptions.RequestException as e:
        # リクエストに関するエラーのハンドリング
        return create_error_response("外部APIへのリクエスト中にエラーが発生しました。")

    except Exception as e:
        # その他の例外発生時のエラーハンドリング
        return create_error_response("予期しないエラーが発生しました。")
