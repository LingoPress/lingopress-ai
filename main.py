import json
import logging
import time
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Header
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor

import parse_message_to_dict
from chatgpt import ChatGpt

from similarity_analysis import SimilarityAnalysis
from youtube_script_extractor import get_youtube_script, post_youtube_script
import aio_pika
import asyncio
import os
from dotenv import load_dotenv

# load .env
load_dotenv()

rabbitmq_host = os.environ.get('RABBITMQ_HOST')
rabbitmq_user = os.environ.get('RABBITMQ_USER')
rabbitmq_password = os.environ.get('RABBITMQ_PASSWORD')

logging.basicConfig(
    level=logging.INFO,  # 로그 레벨 설정
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 로그 출력 형식
    handlers=[
        logging.StreamHandler()  # 콘솔로 로그 출력
    ]
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    loop = asyncio.get_event_loop()
    task = loop.create_task(rabbitmq_listener())
    yield
    task.cancel()
    await task


app = FastAPI(
    title="링고프레스 ai관련 api",
    description="링고프레스에서 사용하는 ai관련 api입니다. chat gpt와 similarity analysis를 제공합니다.",
    version="0.1.0",
    root_path="/v1",
    lifespan=lifespan
)

# RabbitMQ 설정
request_queue_name = "videoProcessingRequestQueue"
response_queue_name = "videoProcessingResponseQueue"

# 비동기 실행을 위한 ThreadPoolExecutor
executor = ThreadPoolExecutor()


async def run_in_threadpool(func, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


class ChatGptRequest(BaseModel):
    original_text: str
    translated_text: str
    word: str
    target_language: str
    user_language: str


# 왜인지 몰라도 E로 시작해야 퀄리티가 좋음.


class ChatGptResponse(BaseModel):
    text: str
    token: int


class SimilarityRequest(BaseModel):
    machineTranslatedText: str
    userTranslatedText: str


class SimilarityResponse(BaseModel):
    similarity: float


class UrlRequest(BaseModel):
    url: str


class UrlResponse(BaseModel):
    script: list


app.router.lifespan_context = lifespan


# 헤더에 api key를 넣어야함
@app.post("/translate/word")
async def translate(sentence: ChatGptRequest, api_key: str = Header(...)):
    chatgpt = ChatGpt(api_key)
    response = chatgpt.translate_kor_word(sentence.original_text + "\n" + sentence.translated_text + "\n" +
                                          sentence.word, target_language=sentence.target_language,
                                          user_language=sentence.user_language)
    print(sentence.original_text + "\n" + sentence.translated_text + "\n" + sentence.word)
    print(response.usage.total_tokens)
    print(response.choices[0].message.content)
    return ChatGptResponse(text=response.choices[0].message.content, token=response.usage.total_tokens)


@app.post("/text_similarity")
async def text_similarity(sentence: SimilarityRequest):
    start = time.time()

    machine = SimilarityAnalysis()
    similarity = machine.get_similarity(sentence.machineTranslatedText,
                                        sentence.userTranslatedText)

    print(f"Time taken: {time.time() - start}")
    return SimilarityResponse(similarity=similarity)


@app.post("/youtube_script")
async def youtube_script(url: UrlRequest):
    print(url)
    script = await run_in_threadpool(get_youtube_script, url.url)
    return {"code": 200, "message": "success", "data": script}


async def rabbitmq_listener():
    try:
        connection = await aio_pika.connect_robust(f"amqp://{rabbitmq_user}:{rabbitmq_password}@{rabbitmq_host}/")
        logging.info("RabbitMQ 연결 성공")
    except Exception as e:
        logging.info(f"RabbitMQ 연결 실패: {e}")
        return

    async with connection:
        try:
            channel = await connection.channel()
            request_queue = await channel.declare_queue(request_queue_name, auto_delete=False)
        except Exception as e:
            logging.warning(f"Queue 설정 실패: {e}")
            return

        async def on_message(message: aio_pika.IncomingMessage):
            async with message.process():
                message_body_decode = message.body.decode()
                try:
                    logging.info(f"Received request: {message_body_decode}")
                    # 요청 메시지 처리 및 응답 전송
                    # 받은 string 메시지 다시 json으로 변환
                    parsed_dict = parse_message_to_dict.parse_message_to_dict(message_body_decode)

                    language = parsed_dict.get('language')
                    video_url = parsed_dict.get('videoUrl')
                    queue_id = parsed_dict.get('id')
                    press_id, is_success = await run_in_threadpool(post_youtube_script, video_url, language)

                    response_message = json.dumps({"queueId": queue_id, "pressId": press_id, "isSuccess": is_success})
                    await channel.default_exchange.publish(
                        aio_pika.Message(body=response_message.encode()),
                        routing_key=response_queue_name,
                    )
                except Exception as e:
                    logging.warning(f"메시지 처리 중 오류 발생: {e}")
                    try:
                        response_message = json.dumps({"queueId": queue_id, "isSuccess": "false"})
                    except Exception as parse_error:
                        logging.error(f"에러 메시지 발송 실패: {parse_error}")

                    await channel.default_exchange.publish(
                        aio_pika.Message(body=response_message.encode()),
                        routing_key=response_queue_name,
                    )

        try:
            await request_queue.consume(on_message)
            print(" [*] Waiting for messages. To exit press CTRL+C")
            await asyncio.Future()  # Keep the connection open
        except Exception as e:
            print(f"메시지 소비 중 오류 발생: {e}")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
