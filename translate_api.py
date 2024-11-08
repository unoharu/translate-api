from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import JSONResponse
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

# サポートされている言語
supported_languages = ['en', 'ja']

# デフォルトのターゲット言語
default_target_lang = '英語または日本語'

class TranslationError(Exception):
    """翻訳エラー用のカスタム例外クラス"""
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(TranslationError)
async def translation_error_handler(request: Request, exc: TranslationError):
    """翻訳エラーのハンドラー"""
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
    """翻訳リクエストを受け取り、バックグラウンドで処理を開始するエンドポイント"""
    logger.info(f"Received text from user ({user_id}): {text}")

    if not text:
        logger.error("エラーが発生しました。本文を入力してください。")
        await send_error(response_url, "エラーが発生しました。本文を入力してください。")
        raise TranslationError(400, "本文を入力してください。")

    # テキストの末尾に言語コードがある場合、それを取り除きターゲット言語を設定
    if text.endswith('en'):
        target_lang = '英語'
        text = text[:-2].strip()
    elif text.endswith('ja'):
        target_lang = '日本語'
        text = text[:-2].strip()
    else:
        target_lang = default_target_lang

    # バックグラウンドタスクとして翻訳処理を追加
    background_tasks.add_task(process_translation, text, response_url, user_id, target_lang)
    return JSONResponse(
        content={
            "response_type": "ephemeral",
            "text": "翻訳を開始しました"
        }
    )

async def process_translation(text: str, response_url: str, user_id: str, target_lang: str):
    """翻訳処理を行い、結果をSlackに送信する関数"""
    try:
        request_system_text = (
            "あなたは通訳者です。\n"
            "あなたはslackから送られてきた文章を自然に翻訳し丁寧語で解答します。\n"
            "説明は必要ないので、翻訳した文章のみ出力してください。\n"
            "Slackの文字形式はそのままにしてください。\n"
            "マークアップ内の文章も翻訳対象です。\n"
            "ただし、コードブロック内は翻訳しないでください。\n"
            "また改行も変更しないでください。"
        )

        request_user_text = (
            f"以下の文章を{target_lang}に翻訳してください。\n\n"
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
                    "text": f"*↓<@{user_id}>さんのメッセージ↓*\n{text}\n\n\n*↓翻訳されたメッセージ↓*\n{translated_text}",
                    "response_type": "in_channel"
                }
            )

    except openai.error.OpenAIError as e:
        logger.error(f"OpenAI APIへのリクエスト中にエラーが発生しました: {str(e)}")
        await send_error(response_url, f"OpenAI APIへのリクエスト中にエラーが発生しました")

    except Exception as e:
        logger.error(f"予期しないエラーが発生しました: {str(e)}")
        await send_error(response_url, f"予期しないエラーが発生しました")

async def send_error(response_url: str, error_message: str):
    """エラーメッセージをSlackに送信する関数"""
    async with httpx.AsyncClient() as client:
        await client.post(
            response_url,
            json={
                "text": error_message,
                "as_user": True
            }
        )