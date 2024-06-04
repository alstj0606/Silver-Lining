# 베이스 이미지 설정
FROM python:3.10

ENV PYTHONUNBUFFERED 1

# GNU gettext 설치
RUN apt-get update && apt-get install -y gettext

# OpenCV와 기타 필요한 패키지 설치
RUN apt-get update && apt-get install -y libgl1-mesa-glx libglib2.0-0

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt 복사 및 패키지 설치
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 사용자 추가 및 권한 설정
RUN adduser -u 5678 --disabled-password --gecos "" appuser && \
    adduser appuser video && \
    chown -R appuser /app

# 애플리케이션 코드 복사
COPY . /app/

# 컨테이너 시작 시 실행할 명령 설정
CMD ["sh", "-c", "python manage.py migrate && python manage.py compilemessages && python manage.py runserver 0.0.0.0:8000"]
