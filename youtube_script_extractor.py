import logging
import re
import time
from datetime import datetime

import spacy
from pytubefix import YouTube
import whisper
import os

from press_db_service import PressDbService

nlp = spacy.load("en_core_web_sm")
abbreviations = {"Dr.", "Mr.", "Mrs.", "Ms.", "Prof.", "Inc."}


# 유튜브 오디오 다운로드
def download_youtube_audio(url, output_path='audio.wav'):
    yt = YouTube(url)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download(filename=output_path)
    return output_path


# Whisper로 음성 인식
def transcribe_audio(audio_path):
    start_time = time.time()

    model = whisper.load_model("base")
    result = model.transcribe(audio_path)
    end_time = time.time()

    # 실행 시간 계산 및 출력
    execution_time = end_time - start_time
    logging.info(f"Whisper Execution time: {execution_time} seconds")
    return result["segments"]


# 구분자 기준으로 텍스트 분리 함수
def split_text_by_delimiters(text):
    sentences = re.split(r'(?<=[.!?]) +', text)
    merged_sentences = []
    i = 0

    while i < len(sentences):
        sentence = sentences[i]
        if any(sentence.endswith(abbrev) for abbrev in abbreviations):
            if i + 1 < len(sentences):
                sentence += ' ' + sentences[i + 1]
                i += 1
        merged_sentences.append(sentence)
        i += 1

    return merged_sentences


# 공백을 하나로 줄이는 함수
def normalize_whitespace(text):
    return re.sub(r'\s+', ' ', text).strip()


# 문장 병합 함수
def merge_segments(segments):
    merged_segments = []
    current_segment = None
    buffer_text = ""

    for segment in segments:
        start = int(segment['start'])
        end = int(segment['end'])
        text = segment['text']

        # 버퍼에 텍스트 추가
        if buffer_text:
            buffer_text += ' ' + text
        else:
            buffer_text = text

        # 구분자를 기준으로 텍스트 분리
        split_sentences = split_text_by_delimiters(buffer_text)

        for sentence in split_sentences[:-1]:  # 마지막 문장은 미완성일 수 있으므로 제외
            normalized_sentence = normalize_whitespace(sentence)
            if current_segment is None:
                current_segment = {'start_sec': start, 'end_sec': end, 'text': normalized_sentence}
            else:
                current_segment['end_sec'] = end
                current_segment['text'] += ' ' + normalized_sentence
            merged_segments.append(current_segment)
            current_segment = None

        # 마지막 미완성 문장을 버퍼에 유지
        buffer_text = split_sentences[-1]

        # Spacy를 사용하여 문장의 경계 파악
        doc = nlp(buffer_text)
        sentences = list(doc.sents)

        # Spacy가 문장으로 인식한 경우 병합된 세그먼트 리스트에 추가
        if len(sentences) > 1 or any([text.endswith(p) for p in ('.', '!', '?')]):
            normalized_buffer_text = normalize_whitespace(buffer_text)
            if current_segment is None:
                current_segment = {'start_sec': start, 'end_sec': end, 'text': normalized_buffer_text}
            else:
                current_segment['end_sec'] = end
                current_segment['text'] += ' ' + normalized_buffer_text
            merged_segments.append(current_segment)
            current_segment = None
            buffer_text = ""

    if buffer_text:
        normalized_buffer_text = normalize_whitespace(buffer_text)
        if current_segment is None:
            current_segment = {'start_sec': start, 'end_sec': end, 'text': normalized_buffer_text}
        else:
            current_segment['end_sec'] = end
            current_segment['text'] += ' ' + normalized_buffer_text
        merged_segments.append(current_segment)

    return merged_segments


def get_youtube_script(url):
    now_time = datetime.today().strftime("%Y%m%d%H%M%S%f")
    audio_path = download_youtube_audio(url, now_time + ".wav")
    segments = transcribe_audio(audio_path)
    os.remove(audio_path)
    return merge_segments(segments)


# 영상 이미지, 제목 가져오기
def get_youtube_info(url):
    yt = YouTube(url)
    return yt.thumbnail_url, yt.title, yt.length


# db에 업로드
def upload_youtube_script_to_db(press):
    press_db_service = PressDbService()
    last_press_id = press_db_service.uploadPressYoutubeDB(press['title'], press['content'], press['url'],
                                                          press['published_at'],
                                                          press['image_url'], press['authors'], press['language'],
                                                          press['publisher'],
                                                          press['access_level'], press['category'])

    logging.info(last_press_id)
    return last_press_id


# 종합
def post_youtube_script(url, language):
    press_db_service = PressDbService()
    exist_press_id = press_db_service.check_exist_url(url)

    # 이미 존재하는 url이면 기존의 press_id 반환
    if exist_press_id is not None:
        return exist_press_id, "true"

    thumbnail, title, length = get_youtube_info(url)
    # 영상 길이가 20분 이상이면 거절
    if length > 1200:
        return None, "false"

    script = get_youtube_script(url)

    press = {
        'title': title,
        'content': script,
        'url': url,
        'published_at': None,
        'image_url': thumbnail,
        'authors': "",
        'language': language,
        "publisher": "",
        'access_level': 'private',
        'category': 'YOUTUBE'
    }
    logging.info(press)
    press_id = upload_youtube_script_to_db(press)
    return press_id, "true"

# 유튜브 링크
# url = "https://www.youtube.com/watch?v=XvCoQ8hxRsY"


# 문장 병합

# 결과 출력
#for segment in merged_segments:
#    start = segment['start']
#    end = segment['end']
#    text = segment['text']
#    print(f"{start}초 - {end}초: {text}")
# # 임시 파일 삭제
#os.remove(audio_path)
