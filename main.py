from fastapi import FastAPI, Header
from pydantic import BaseModel

from chatgpt import ChatGpt

app = FastAPI()


class ChatGptRequest(BaseModel):
    original_text: str
    word: str


class ChatGptResponse(BaseModel):
    text: str
    token: int


# 헤더에 api key를 넣어야함
@app.post("/translate/word")
async def translate(sentence: ChatGptRequest, api_key: str = Header(...)):
    chatgpt = ChatGpt(api_key)
    response = chatgpt.translate_kor_word(sentence.original_text + "\n" + sentence.word)
    print(sentence.original_text + "\n" + sentence.word)
    print(response.usage.total_tokens)
    print(response.choices[0].message.content)
    return ChatGptResponse(text=response.choices[0].message.content, token=response.usage.total_tokens)
