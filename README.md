# fax_api

api for fax

### 概要

- [Hylafax](https://www.hylafax.org/)がインストールされている環境で、FAX の送受信を API 経由で行うものです。
- ~~フロントエンドは未対応ですが、~~ SwaggerUI によりブラウザから操作可能です。
  ![](swaggerui.png)
- より簡易に扱えるように、[フロントエンド（HylaFAX 操作ツール）](https://github.com/katsumin/fax_app)を作成しました。

### 環境

- Hylafax がインストールされていること
- Python3.8 以上がインストールされていること
- 使用ライブラリ
  - Flask
  - Flask-RESTX
- [RasPBX](http://www.raspbx.org/)の[FAX 機能](http://www.raspbx.org/documentation/#fax)がインストールされた RaspberryPI での動作を確認しています。

### インストール

```sh
user@raspbx:~/fax_api $ echo 'RcvFmt: "%Y,%p,%s,%h,%f"' > ~/.hylarc
user@raspbx:~/fax_api $ . .venv/bin/activate
(.venv) user@raspbx:~/fax_api $ pip install -r requirements.txt
```

- 受信状態取得結果のフォーマットを定義するため、`~/.hylarc`の記述が追加になりました。

### 実行

- 下記コマンドで実行し、`http://IPアドレス:5000`でブラウザからアクセス。

```sh
(.venv) user@raspbx:~/fax_api $ tmux new-session -d 'python src/fax_api.py'
```

### 機能

1. FAX 送信
   - パラメータ
     - 送信先電話番号
     - 送信ファイル
1. FAX 送信状態取得
   - パラメータなし
1. FAX 送信ジョブの削除
   - パラメータ
     - 送信ジョブ ID（FAX 送信のレスポンスから取得可能）
1. FAX 受信状態取得
   - パラメータなし
1. FAX 受信ファイル取得
   - パラメータ
     - 受信ファイル名
