import os
from openai import OpenAI


class ChatGpt:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)

    def create_chat(self, model, messages, temperature, max_tokens, top_p, frequency_penalty, presence_penalty):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty
        )

    def translate_kor_word(self, sentence, target_language, user_language):
        content = ("The first line is a sentence, the second line is a translation sentence, "
                   "and the third line is " + target_language + " word. "
                   "analyzes translation sentence and outputs just what the word means in " + user_language + ".")

        print("content: ", content)
        response = self.create_chat(
            model="gpt-3.5-turbo-0125",
            messages=[
                {
                    "role": "system",
                    "content": content
                },
                {
                    "role": "user",
                    "content": sentence
                }

            ],
            temperature=0,
            max_tokens=512,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )

        return response
