# Dockerfile 내용

# 베이스 이미지 설정
FROM python:3.10

# 환경 변수 설정
ENV PYTHONUNBUFFERED 1

# GNU Gettext와 OpenCV 설치
RUN apt-get update && apt-get install -y \
    gettext \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 애플리케이션 코드 복사
COPY . /app/
