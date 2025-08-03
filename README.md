# 起動方法

## 必要な環境
- Python 3.9以上
- pip

## セットアップ
1. 仮想環境を作成します。
   ```bash
   python -m venv .venv
   ```
2. 仮想環境を有効化します。
   - macOS/Linux:
     ```bash
     source .venv/bin/activate
     ```
   - Windows:
     ```bash
     .venv\Scripts\activate
     ```
3. 必要なパッケージをインストールします。
   ```bash
   pip install -r requirements.txt
   ```

## サーバーの起動
以下のコマンドでFastAPIサーバーを起動します。
```bash
uvicorn main:app --reload
```

サーバーはデフォルトで `http://127.0.0.1:8000` でアクセス可能です。