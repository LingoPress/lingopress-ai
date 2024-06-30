import time

from pytube import YouTube
import whisper
import os


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
    print(f"Execution time: {execution_time} seconds")
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
            current_segment = {'start': start, 'end': end, 'text': text}
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
    audio_path = download_youtube_audio(url)
    segments = transcribe_audio(audio_path)
    os.remove(audio_path)
    return merge_segments(segments)

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
