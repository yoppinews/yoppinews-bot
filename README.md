yoppinews-bot
===============


[![CircleCI](https://circleci.com/gh/yoppinews/yoppinews-bot/tree/develop.svg?style=svg)](https://circleci.com/gh/yoppinews/yoppinews-bot/tree/develop)

[@yoppinews](https://twitter.com/yoppinews) にて使われている関連ツイート検出 bot エンジン

# yoppinews-bot とは

- 設定ファイルに指定された Twitter リストを毎分巡回し、以下のような条件にマッチするツイートをリツイートします
  - 設定ファイルにて指定したキーワードを含むツイート
  - 設定ファイルにて指定したキーワードを含むウェブページの URL 付きのツイート
  - 設定ファイルにて指定した画像と類似する画像付きのツイート
- リツイートの条件をリスト単位で細かく制御可能で、競合する条件に対しては否定条件が優先されます
  - 常にリツイートする
  - リプライは検知対象から外す
  - リツイートは検知対象から外す
  - 引用リツイートの引用先テキストは検知対象から外す
  - 画像の検出は行わない
  - URL の検出は行わない
- 開発・利用はどなたでも可能です
  - ライセンスは MIT です
  - 機能追加・不具合修正に際しては Issue の起票からはじめていただけると助かります


# 導入方法
## 1. リポジトリのクローンと設定ファイルの作成

- `git clone`
- `cd yoppinews-bot`
- `cp .env.template .env.{dev|prod}`

## 2. 環境変数ファイルの更新

デプロイおよび bot 稼働に必要な情報を設定ファイルに記載する

- `vi .env.{dev|prod}`


## 3. アプリケーション設定ファイルの更新


- `cp config.template.yaml config.{dev|prod}.yaml`
- `vi config.{dev|prod}.yaml`
- `./scripts/update-config`


## 4. デプロイ

`-f` オプションは pip モジュールや関連するモジュールの解決を行う際に使います

```
./scripts/deploy -f [dev|prod]
```


# 開発・運用上の手順チートシート
## 開発の環境の整備

```
pip install -r requirements.txt
```

## ユニットテスト

```
python -m pytest tests/ -v
```

## ローカル実行

```
./scripts/envjson-gen
docker-compose up -d
awslocal s3api create-bucket --bucket news-bot
awslocal s3 cp ./config.dev.yaml s3://news-bot/config.json
awslocal dynamodb create-table --table-name CollectTweets --cli-input-json file://ddb_table.json

sam build
sam local invoke CollectTweetsFunction \
  --no-event --env-vars ./env.dev.json \
  --docker-network `docker network ls | grep yoppinews-bot | awk '{print $1}'`
```

## アプリケーションのデプロイ

```
./scripts/deploy [dev|prod]
```
