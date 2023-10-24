# ubuntu 환경 설정(ssh 연결 필요할때)
FROM ubuntu/python3115/ssh/gdal:latest

# amazonlinux 환경 설정(실제)
#FROM amazonlinux

# 컨테이너 관리자
MAINTAINER yw <cafejari2023@cafejari.co.kr>

# 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV SECRET_KEY: ${SECRET_KEY}
ENV DB_NAME: ${DB_NAME}
ENV DB_USER: ${DB_USER}
ENV DB_PASSWORD: ${DB_PASSWORD}

# 우분투 설정 과정
#RUN apt update -y && apt upgrade -y && \
#    apt install -y openssh-server software-properties-common cron curl && \
#    add-apt-repository ppa:deadsnakes/ppa && \
#    apt install -y python3.11 && \
#    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
#    curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
#    apt-get install --reinstall python3-apt
#    apt-get install binutils libproj-dev gdal-bin

# amazonlinux 설정 과정
#RUN yum update -y && yum upgrade -y && \
#    yum install -y wget tar gzip zlib-devel bzip2-devel cronie make gcc && \
#    wget https://www.python.org/ftp/python/3.11.4/Python-3.11.4.tgz && \
#    tar xzf Python-3.11.4.tgz && \
#    cd /Python-3.11.4 && \
#    ./configure --enable-optimizations && \
#    make altinstall && \
#    rm -f /opt/Python-3.11.4.tgz
#    update-alternatives --install /usr/bin/python3 python3 /usr/bin/Python-3.11.4/python 1

# 복사할 파일을 위한 디렉토리 생성, 이동
RUN mkdir /cafejari
WORKDIR /cafejari

# 필요한 라이브러리 설치
ADD . /cafejari/
RUN pip3 install --upgrade pip && pip3 install -r requirements.txt
RUN pip3 install boto3

# 컨테이너에서 실행될 명령어
#ENTRYPOINT python3 manage.py makemigrations && python3 manage.py migrate && gunicorn cafejari.wsgi -b 0.0.0.0:8000:application

# 실행상태 유지
#ENTRYPOINT tail -f /dev/null