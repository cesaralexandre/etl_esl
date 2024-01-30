FROM python:3.12-slim

RUN useradd -ms /bin/bash python

USER python

WORKDIR /home/python/app

COPY . .

RUN pip install --upgrade pip && pip install -r requirements.txt

CMD [ "tail", "-f", "/dev/null" ]