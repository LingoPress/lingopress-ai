FROM python:3.12-slim

WORKDIR /app/

COPY ./*.py /app/
COPY ./requirements.txt /app/
COPY ./model_all-MiniLM-L6-v2 /app/model_all-MiniLM-L6-v2/

RUN pip install -r requirements.txt

RUN apt update && apt install ffmpeg -y

CMD uvicorn --host=0.0.0.0 --port 8000 main:app