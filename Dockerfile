FROM python:3.12-slim

WORKDIR /app/

COPY ./requirements.txt /app/

RUN pip install -r requirements.txt

RUN apt update && apt install ffmpeg -y

COPY ./*.py /app/
COPY ./model_all-MiniLM-L6-v2 /app/model_all-MiniLM-L6-v2/


CMD uvicorn --host=0.0.0.0 --port 8000 main:app