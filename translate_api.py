from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse, PlainTextResponse
import openai
import os
from dotenv import load_dotenv
import logging
import httpx

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# .envファイルから環境変数を読み込む
load_dotenv()

# OpenAI APIキー設定
openai.api_key = os.getenv('OPENAI_API_KEY')

app = FastAPI()

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
async def translate_text(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
    response_url: str = Form(...),
    user_id: str = Form(...)
    ):
    logger.info(f"Received text from user ({user_id}): {text}")

    if not text:
        logger.error("エラーが発生しました。本文を入力してください。")
        await send_error(response_url, "エラーが発生しました。本文を入力してください。")
        raise TranslationError(400, "本文を入力してください。")

    background_tasks.add_task(process_translation, text, response_url, user_id)
    return JSONResponse(
    content={
        "response_type": "ephemeral",
        "text": f"翻訳を開始しました"
    }
)

async def process_translation(text: str, response_url: str, user_id: str):
    try:
        request_system_text = (
            "あなたは通訳者です。\n"
            "あなたはslackから送られてきた文章を自然に翻訳し丁寧語で解答します。\n"
            "説明は必要ないので、翻訳した文章のみ出力してください。\n"
            "マークアップ内の文章も翻訳対象です。\n"
            "ただし、コードブロック内は翻訳しないでください。\n"
            "また改行も変更しないでください。"
        )

        request_user_text = (
            f"以下の文章を英語または日本語に翻訳してください。\n\n"
            f"{text}"
        )

        logger.info(f"Requesting translation for text: {text}")

        # OpenAI APIにリクエストを送信
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": request_system_text},
                {"role": "user", "content": request_user_text}
            ]
        )

        # OpenAI APIからのレスポンスを取得
        translated_text = response['choices'][0]['message']['content']
        logger.info(f"Translated text: {translated_text}")

        # 翻訳結果をSlackに送信
        async with httpx.AsyncClient() as client:
            await client.post(
                response_url,
                json={
                    "text": f"*↓<@{user_id}>さんのメッセージ↓*\n{text}\n\n\n*↓翻訳されたメッセージ↓*\n\n\n{translated_text}",
                    "response_type": "in_channel"
                }
            )


    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI APIへのリクエスト中にエラーが発生しました: {str(e)}")
        await send_error(response_url, f"OpenAI APIへのリクエスト中にエラーが発生しました: {str(e)}")

    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        await send_error(response_url, f"予期しないエラーが発生しました: {str(e)}")

async def send_error(response_url: str, error_message: str):
    async with httpx.AsyncClient() as client:
        await client.post(
            response_url,
            json={
                "text": error_message,
                "as_user": True
            }
        )