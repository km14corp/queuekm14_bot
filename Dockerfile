FROM python:3.10.2-alpine3.15

RUN apk update && apk add python3-dev \
                        gcc \
                        libc-dev

WORKDIR /usr/app/src

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

CMD [ "python", "./main.py"]
