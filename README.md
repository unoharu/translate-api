# translate-api
## 概要
### Slackのメッセージを自動で翻訳し送信するAPI

### 構成
<img width="1367" alt="アーキテクチャ" src="https://github.com/user-attachments/assets/ac83e438-c38b-47cd-a82c-494920041739">

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

<img width="951" alt="ngrokのurl" src="https://github.com/user-attachments/assets/1ff84ce4-93ef-47f4-98f6-1f5149f76b97">

↑の場合 https://aae9-180-43-3-253.ngrok-free.app/translate をSlack APIのRequestURLに設定

#### 注意点:
ngrokを再起動するたびにURLが変更されるため、SlackのスラッシュコマンドのRequestURLもその都度更新する必要あり

### Slack APIの設定

#### スラッシュコマンドの設定
<img width="400" alt="スラッシュコマンド設定" src="https://github.com/user-attachments/assets/514b6509-525f-43f7-85d8-63500f915019">



#### スコープの設定
<img width="400" alt="スコープ設定" src="https://github.com/user-attachments/assets/62d50f84-e107-4941-9e85-8eaca77bf45e">


## 実行デモ
![SlackAPIデモGIF](https://github.com/user-attachments/assets/9c54006f-90c1-4257-9757-79bc5e0714af)

