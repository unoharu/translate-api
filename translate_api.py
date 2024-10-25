from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse, PlainTextResponse
import openai
import os
from dotenv import load_dotenv
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキー設定
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

supported_languages = ['en', 'ja']

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
async def translate_text(text: str = Form(...)):
    try:
        logger.info(f"Received text: {text}")

        # 言語コードを抽出
        if text.endswith('en'):
            target_lang = 'en'
            text = text[:-2].strip()
        elif text.endswith('ja'):
            target_lang = 'ja'
            text = text[:-2].strip()
        else:
            logger.error("言語コードが見つかりません。")
            raise TranslationError(400, f"言語コードが見つかりません。{supported_languages} のいずれかを指定してください。")

        if not text and not target_lang:
            logger.error("本文と言語が指定されていません。")
            raise TranslationError(400, f"本文と言語が指定されていません。本文と{supported_languages} のいずれかを指定してください。")

        if not target_lang:
            logger.error("言語が指定されていません。")
            raise TranslationError(400, f"言語が指定されていません。{supported_languages} のいずれかを指定してください。")

        if target_lang not in supported_languages:
            logger.error(f"{target_lang} は対応していない言語です。")
            raise TranslationError(400, f"{target_lang} は対応していない言語です。{supported_languages}のいずれかを指定してください。")

        if not text:
            logger.error("本文を入力してください。")
            raise TranslationError(400, "本文を入力してください。")
        
        if target_lang == "ja":
            trans_lang = "日本語"
        elif target_lang == "en":
            trans_lang = "英語"

        request_system_text = (
            "あなたは通訳者です。\n"
            "あなたはslackから送られてきた文章を自然に翻訳し丁寧語で解答します。\n"
            "説明は必要ないので、翻訳した文章のみ出力してください。\n"
            "マークアップ内の文章も翻訳対象です。\n"
            "ただし、コードブロックは変換しないでください。\n"
        )

        request_user_text = (
            f"以下の文章を{trans_lang}に翻訳してください。\n\n"
            f"{text}"
        )

        logger.info(f"Requesting translation for text: {text} to {trans_lang}")

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
        logger.info(f"Translated text: {translated_text}")
        return PlainTextResponse(translated_text)

    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI APIへのリクエスト中にエラーが発生しました: {str(e)}")
        raise TranslationError(500, f"OpenAI APIへのリクエスト中にエラーが発生しました: {str(e)}")

    except TranslationError as e:
        logger.error(f"Translation error: {str(e)}")
        raise e

    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        raise TranslationError(500, f"予期しないエラーが発生しました: {str(e)}")