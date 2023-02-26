FROM python:3.10.6
WORKDIR /app
COPY ./ /app/
RUN pip install --no-cache-dir --upgrade -r requirements.txt -i http://mirrors.tencentyun.com/pypi/simple --trusted-host mirrors.tencentyun.com
RUN rm requirements.txt
CMD ["python", "bot.py"]