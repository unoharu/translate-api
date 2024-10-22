from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests

app = FastAPI()

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
        if not text and not target_lang:
            raise TranslationError(400, f"本文と言語が指定されていません。本文と{supported_languages} のいずれかを指定してください。")

        if not target_lang:
            raise TranslationError(400, f"言語が指定されていません。{supported_languages} のいずれかを指定してください。")

        if target_lang not in supported_languages:
            raise TranslationError(400, f"{target_lang} は対応していない言語です。{supported_languages}のいずれかを指定してください。")

        if not text:
            raise TranslationError(400, "本文を入力してください。")

        # モックAPIのURL（モックAPIにリクエストを転送）
        mock_api_url = "http://localhost:8001/v1/chat/completions"

        request_text = f'''
            {target_lang}に翻訳してください。
            ただし、slackからの文章なのでメンションやメールアドレス、リンクなど特別な意味を持つものは変換しないでください。
            
            ↓翻訳対象のテキスト↓
            {text}
        '''

        # モックAPIに転送するデータを整形
        payload = {
            "model": "gpt-3.5-turbo",  # 使いたいモデル名
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

    except requests.exceptions.RequestException:
        raise TranslationError(500, "外部APIへのリクエスト中にエラーが発生しました。")

    except TranslationError as e:
        raise e

    except Exception:
        raise TranslationError(500, "予期しないエラーが発生しました。")