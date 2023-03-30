FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt  -i https://mirrors.aliyun.com/pypi/simple

COPY . .

CMD [ "python", "./app.py" ]