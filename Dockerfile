FROM python:3.10

WORKDIR /usr/src/app

RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

CMD [ "python", "./app.py" ]