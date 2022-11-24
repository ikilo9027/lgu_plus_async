FROM python:3.8.13-slim-buster

SHELL ["/bin/bash", "-c"]

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y locales sudo libb64-dev libgl1-mesa-glx git libglib2.0-0 && \
    locale-gen ko_KR.UTF-8 && \
    #    pip3 install -r requirements.txt
    pip3 install numpy opencv-python tritonclient[all] fastapi && \
    pip3 install uvicorn[standard] psycopg2-binary python-multipart && \
    pip3 install requests SQLAlchemy pydantic && \
    pip3 install Pillow && \
    pip3 install loguru && \
    pip3 install pytz && \
    pip3 install python-dateutil && \
    pip3 install celery && \
    pip3 install redis

COPY . /app

ENV LC_ALL ko_KR.UTF-8

WORKDIR /app

RUN ["/bin/bash"]

# CMD ["python","-m","uvicorn" ,"main:app", "--host", "0.0.0.0", "--port", "4110", "--workers", "4"]