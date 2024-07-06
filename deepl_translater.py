import deepl
import os
from dotenv import load_dotenv

# load .env
load_dotenv()

auth_key = os.environ.get('DEEPL_AUTH_KEY')
translator = deepl.Translator(auth_key)


def translate_press_content_line(original_content_line, target_lang="KO"):
    if len(original_content_line) == 0:
        print("빈 라인입니다.")
        return ""
    # deepL API를 이용한 번역

    # deepl에는 en-us로 넣어줘야 번역함.
    target_lang = target_lang
    if target_lang == "en":
        target_lang = "en-us"

    result = translator.translate_text(original_content_line, target_lang=target_lang)

    print(result.text)
    return result.text
