# translate-api
## 概要
### Slackのメッセージを自動で翻訳し送信するAPI

### 構成
<img width="1367" alt="アーキテクチャ" src="https://github.com/user-attachments/assets/539cafa6-6d67-4d60-9adf-734825828309">

## ローカル環境での実行方法
### 仮想環境の作成
```
python3 -m venv .venv
```
### 仮想環境のアクティベート
Windowsの場合:
```
.venv\Scripts\activate.bat
```

macOS / Linuxの場合:
```
source .venv/bin/activate
```

### 必要なパッケージのインストール
```
pip install -r requirements.txt
```

### サーバーの実行
uvicornを使用してサーバーを起動
```
uvicorn translate_api:app --host 127.0.0.1 --port 8000
```

ngrokを使用してローカルサーバーを公開
```
ngrok http 8000
```
このコマンドで、Slackからアクセス可能なパブリックURLが作成される
URLをSlack APIのRequestURLに設定

#### 注意点:
ngrokを再起動するたびにURLが変更されるため、SlackのスラッシュコマンドのRequestURLもその都度更新する必要あり

## 実行デモ
![実行デモ](https://github.com/user-attachments/assets/39932ac0-8e0f-4abc-a1ef-ad08ba5cbe8f)
