FROM python:3.10-slim

ARG actionType

WORKDIR /usr/src/app

COPY requirements.txt ./
#1)http://mirrors.aliyun.com/pypi/simple/ 阿里云
#2)https://pypi.mirrors.ustc.edu.cn/simple/  中国科技大学
#3) http://pypi.douban.com/simple/  豆瓣
#4) https://pypi.tuna.tsinghua.edu.cn/simple/ 清华大学
#5)  http://pypi.mirrors.ustc.edu.cn/simple/ 中国科学技术大学
RUN pip install -r requirements.txt  -i https://pypi.mirrors.ustc.edu.cn/simple/ # 中国科技大学

COPY . .

CMD [ "python", "./app.py ${actionType}" ]