# YouTube-Scraping

## 設定

1. [docker](https://www.docker.com/) をインストール
　
2. dockerイメージをpull

```bash
# Linux
sudo docker pull scrapinghub/splash
# Mac
docker pull scrapinghub/splash
```
　
3. コンテナを作成・起動

```bash
# Linux
sudo docker run -it -p 8050:8050 scrapinghub/splash
# Mac
docker run -it -p 8050:8050 scrapinghub/splash
```

http://localhost:8050/ にアクセスして起動確認

# HTTP API
Splashでは，HTTP APIを使うことで簡単にページ情報を取得できます。ここではその一例を紹介しますが，より詳しく知りたい方は[公式ドキュメント](https://splash.readthedocs.io/en/stable/api.html)を御覧ください。
