import time

from fastapi import FastAPI, Header
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import asyncio

from chatgpt import ChatGpt

from similarity_analysis import SimilarityAnalysis
from youtube_script_extractor import get_youtube_script

app = FastAPI(
    title="링고프레스 ai관련 api",
    description="링고프레스에서 사용하는 ai관련 api입니다. chat gpt와 similarity analysis를 제공합니다.",
    version="0.1.0",
    root_path="/v1",
)

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
