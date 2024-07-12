import logging
import time
from datetime import datetime

from pytube import YouTube
import whisper
import os

from press_db_service import PressDbService


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


# 문장 병합 함수
def merge_segments(segments):
    merged_segments = []
    current_segment = None

    for segment in segments:
        start = int(segment['start'])
        end = int(segment['end'])
        text = segment['text']

        if current_segment is None:
            current_segment = {'start_sec': start, 'end_sec': end, 'text': text}
        else:
            current_segment['end'] = end
            current_segment['text'] = current_segment['text'].rstrip() + ' ' + text  # 끝 공백 제거 후 결합

        if text.endswith(('.', '!', '?')):
            merged_segments.append(current_segment)
            current_segment = None

    if current_segment is not None:
        merged_segments.append(current_segment)

    return merged_segments


def get_youtube_script(url):
    now_time = datetime.today().strftime("%Y%m%d%H%M%S%f")
    audio_path = download_youtube_audio(url, now_time+".wav")
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
    last_press_id = press_db_service.uploadPressYoutubeDB(press['title'], press['content'], press['url'], press['published_at'],
                                          press['image_url'], press['authors'], press['language'], press['publisher'],
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
