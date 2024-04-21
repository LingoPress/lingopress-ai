from fastapi import FastAPI, Header
from pydantic import BaseModel

from chatgpt import ChatGpt

app = FastAPI()


class ChatGptRequest(BaseModel):
    original_text: str
    translated_text: str
    word: str
    original_language: str = "English"
# 왜인지 몰라도 E로 시작해야 퀄리티가 좋음.


class ChatGptResponse(BaseModel):
    text: str
    token: int


# 헤더에 api key를 넣어야함
@app.post("/translate/word")
async def translate(sentence: ChatGptRequest, api_key: str = Header(...)):
    chatgpt = ChatGpt(api_key)
    response = chatgpt.translate_kor_word(sentence.original_text + "\n" + sentence.translated_text + "\n" +
                                          sentence.word, original_language=sentence.original_language)
    print(sentence.original_text + "\n" + sentence.translated_text + "\n" + sentence.word)
    print(response.usage.total_tokens)
    print(response.choices[0].message.content)
    return ChatGptResponse(text=response.choices[0].message.content, token=response.usage.total_tokens)
