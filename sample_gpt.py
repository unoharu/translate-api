from fastapi import FastAPI

app = FastAPI()

@app.post("/v1/chat/completions")
async def mock_chat_completion(request: dict):
    return {
        "id": "chatcmpl-1234567890",
        "object": "chat.completion",
        "created": 1697042000,
        "model": request["model"],
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "こんにちは、世界！"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 9,
            "completion_tokens": 7,
            "total_tokens": 16
        }
    }
