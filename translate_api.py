from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
import os
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキー設定
openai.api_key = os.getenv('OPENAI_API_KEY')

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
async def translate_text(data: TranslationRequest):
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
        
        if target_lang == "ja":
            trans_lang = "日本語"
        elif target_lang == "en":
            trans_lang = "英語"

        request_system_text = (
            "あなたは通訳者です。\n"
            "文章を自然に翻訳し解答します。\n"
            "説明は必要ないので、翻訳した文章のみ出力してください。\n"
            "また、人物だと思われるものには「さん」をつけてください。"
        )

        request_user_text = (
            f"以下の文章を{trans_lang}に翻訳してください。\n"
            "ただし、メンションやメールアドレス、リンクなど特別な意味を持つものは変換しないでください。\n\n"
            f"{text}"
        )

        # OpenAI APIにリクエストを送信
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": request_system_text},
                {"role": "user", "content": request_user_text}
            ]
        )

        # OpenAI APIからのレスポンスを取得
        translated_text = response['choices'][0]['message']['content']
        return {"status": "success", "translated_text": translated_text}

    except openai.error.OpenAIError as e:
        raise TranslationError(500, f"OpenAI APIへのリクエスト中にエラーが発生しました: {str(e)}")

    except TranslationError as e:
        raise e

    except Exception as e:
        raise TranslationError(500, f"予期しないエラーが発生しました: {str(e)}")