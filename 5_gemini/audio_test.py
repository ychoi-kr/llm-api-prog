import google.generativeai as genai
from datetime import datetime
import pytz

def convert_to_kst(utc_time):
    fmt_utc_time = datetime.fromisoformat(str(utc_time))
    kst = pytz.timezone("Asia/Seoul")
    kst_time = fmt_utc_time.astimezone(kst)
    return kst_time.strftime("%Y-%m-%d %H:%M:%S.%f")

model = genai.GenerativeModel('gemini-1.5-flash-latest')
path = '../data/5-things-to-know-from-GoogleIO-2024.mp3'

# File API로 오디오 파일 업로드
audio_file = genai.upload_file(path=path)

# 프롬프트에 오디오 파일 포함하여 응답 생성
response = model.generate_content(["한국어로 요약해줘.", audio_file])
print(response.text)
print(f"생성시각: {convert_to_kst(audio_file.create_time)}")
print(f"만료시각: {convert_to_kst(audio_file.expiration_time)}")
audio_file.delete()