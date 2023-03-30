FROM python:3.10

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install ddddocr -i https://pypi.tuna.tsinghua.edu.cn/simple/

COPY . .

CMD [ "python", "./app.py" ]