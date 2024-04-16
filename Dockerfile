#FROM python:3.10-slim
#
#ENV PYTHONUNBUFFERED True
#
#ENV APP_HOME /app
#WORKDIR $APP_HOME
#COPY . ./
#
#RUN pip install --no-cache-dir -r requirements.txt
#
#CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app


#ローカル用
# Pythonランタイムを親イメージとして使用
FROM python:3.11

# 作業ディレクトリを/appに設定
WORKDIR /Arcaea_Tier

# 現在のディレクトリの内容をコンテナ内の/appにコピー
COPY . /Arcaea_Tier

# requirements.txtで指定された必要なパッケージをインストール
RUN pip install -r requirements.txt

# コンテナ起動時にapp.pyを実行
CMD ["python", "app.py"]