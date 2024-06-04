FROM python:3.10

ENV PYTHONUNBUFFERED 1

# GNU gettext 설치
RUN apt-get update && apt-get install -y gettext

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . /app/

RUN apt-get update && apt-get install libgl1 -y
