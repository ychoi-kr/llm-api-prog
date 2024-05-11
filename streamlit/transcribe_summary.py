import streamlit as st
from pytube import YouTube
from openai import BadRequestError, OpenAI
import os
import tempfile

# API 키 설정
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def get_video_info(url):
    yt = YouTube(url)
    title = yt.title
    # pytube에서 description을 가져오지 못하는 경우, fallback으로 description을 가져옴    
    description = yt.description if yt.description else get_description_fallback(url)
    return title, description

# https://github.com/pytube/pytube/issues/1626#issuecomment-1775501965
def get_description_fallback(url):
    yt = YouTube(url)
    for n in range(6):
        try:
            description =  yt.initial_data["engagementPanels"][n]["engagementPanelSectionListRenderer"]["content"]["structuredDescriptionContentRenderer"]["items"][1]["expandableVideoDescriptionBodyRenderer"]["attributedDescriptionBodyText"]["content"]            
            return description
        except:
            continue
    return False

def download_audio(url):
    video = YouTube(url).streams.filter(only_audio=True).first().download()
    return video

def trim_file_to_size(filepath, max_size):
    file_size = os.path.getsize(filepath)

    if file_size <= max_size:
        return filepath

    # 원본 파일의 확장자를 유지하기 위해 파일명에서 확장자 추출
    _, file_ext = os.path.splitext(filepath)

    # 파일 크기가 최대 크기를 초과하는 경우, 처리 로직
    with open(filepath, "rb") as file:
        data = file.read(max_size)

    # 임시 파일 생성 및 데이터 쓰기
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=file_ext)
    temp_file.write(data)
    temp_file.close()

    return temp_file.name

def transcribe(audio_filepath, response_format='text', prompt=None):
    # 파일 크기 제한 (25MB)
    # Maximum content size limit는 26214400이지만 여유를 두기 위해 26210000으로 설정
    MAX_FILE_SIZE = 26210000

    # 파일 크기를 확인하고 필요한 경우 자르기
    trimmed_audio_filepath = trim_file_to_size(audio_filepath, MAX_FILE_SIZE)

    # 받아쓰기
    with open(trimmed_audio_filepath, "rb") as file:
        transcript = client.audio.transcriptions.create(
            file=file,
            model="whisper-1",
            response_format=response_format,
            prompt=prompt,
        )

    st.session_state.transcript = transcript

    # 임시 파일이 생성되었을 경우 삭제
    if trimmed_audio_filepath != audio_filepath:
        os.remove(trimmed_audio_filepath)

def summarize(transcript, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system",
             "content": f"First, summarize the transcription briefly in the same language in which the original dialogue was spoken. And then, if it is not in Korean, write a Korean summary as well.\n\nFORMAT:\n<summary_in_original_language>\n\nKorean summary:\n<korean_summary>"},
            {"role": "user", "content": transcript},
        ],
    )
    return response.choices[0].message.content

# Streamlit UI 구성
st.title("Video Subtitles and Summary Generator")

url = st.text_input("Enter Video URL:")

# 유튜브 영상 정보 가져오기 버튼
if st.button("Load Video Info"):
    if url:
        title, description = get_video_info(url)
        st.session_state.video_info = f"Title: {title}\nDescription: {description}"
    else:
        st.error("Please enter a valid YouTube URL.")

# 영상 정보를 프롬프트에 표시
prompt = st.text_area("What's the video about? (Optional)", value=st.session_state.get('video_info', ''), help="Provide a brief description of the video or include specific terms like unique names and key topics to enhance accuracy. This can include spelling out hard-to-distinguish proper nouns.")
response_format = st.selectbox("Select Output Format:", ('text', 'srt', 'vtt'))

# 세션 상태 초기화
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""

if st.button("Generate Subtitles"):
    if url:
        with st.spinner('Downloading and transcribing video... This may take a while.'):
            filename = download_audio(url)
            transcribe(filename, response_format=response_format, prompt=prompt)
            os.remove(filename)  # 다운로드한 파일 삭제
        st.success('Done! Subtitles have been generated.')
    else:
        st.error("Please enter a URL.")

# 자막이 있을 경우, 자막 필드를 항상 표시
if st.session_state.transcript:
    st.text_area("Subtitles:", value=st.session_state.transcript, height=300)

# "Summarize" 버튼 처리 로직
if st.button("Summarize"):
    if st.session_state.transcript:
        try:
            # 요약 시도
            st.session_state.summary = summarize(st.session_state.transcript)
        except BadRequestError as e:
            # BadRequestError 발생 시 다른 모델로 재시도
            st.session_state.summary = \
                summarize(st.session_state.transcript, model="gpt-4-turbo-preview")

# 요약문이 있을 경우, 요약문 필드를 표시
if st.session_state.summary:
    st.text_area("Summary:", value=st.session_state.summary, height=150)
