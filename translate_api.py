from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

app = FastAPI()

# 対応する言語リスト
supported_languages = ['en', 'ja']

class TranslationRequest(BaseModel):
    text: str
    target_lang: str

class TranslationError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(TranslationError)
async def translation_error_handler(request: Request, exc: TranslationError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "error_message": exc.detail}
    )

@app.post("/translate")
def translate_text(data: TranslationRequest):
    target_lang = data.target_lang
    text = data.text
    
    try:
        # textとtarget_langの両方が未入力の場合
        if not text and not target_lang:
            raise TranslationError(400, f"textとtarget_langの両方が指定されていません。textと{supported_languages} のいずれかを指定してください。")

        # target_langが未入力の場合
        if not target_lang:
            raise TranslationError(400, f"言語が指定されていません。{supported_languages} のいずれかを指定してください。")

        # 対応していない言語がリクエストされた場合
        if target_lang not in supported_languages:
            raise TranslationError(400, f"{target_lang} は対応していない言語です。{supported_languages}のいずれかを指定してください。")

        # 翻訳するテキストが未入力の場合
        if not text:
            raise TranslationError(400, "textを入力してください。")

        # モックAPIのURL（モックAPIにリクエストを転送）
        mock_api_url = "http://localhost:8001/v1/chat/completions"

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

            raise TranslationError(response.status_code, error_message)

    except requests.exceptions.RequestException:
        # リクエストに関するエラーのハンドリング
        raise TranslationError(500, "外部APIへのリクエスト中にエラーが発生しました。")

    except TranslationError as e:
        raise e

    except Exception:
        # その他の例外発生時のエラーハンドリング
        raise TranslationError(500, "予期しないエラーが発生しました。")