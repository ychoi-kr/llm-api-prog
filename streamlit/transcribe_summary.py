import streamlit as st
from pytube import YouTube
from openai import BadRequestError, OpenAI
import os
import tempfile


# 클라이언트 초기화
openai_client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)
upstage_client = OpenAI(
    api_key=st.secrets["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1/solar"
)

def get_video_info(url):
    yt = YouTube(url)
    title = yt.title
    # pytube에서 description을 가져오지 못하는 경우, fallback으로 description을 가져옴
    description = yt.description if yt.description else get_description_fallback(url)
    print(f"\nTitle: {title}\nDescription: {description}")
    return title, description

# https://github.com/pytube/pytube/issues/1626#issuecomment-1775501965
def get_description_fallback(url):
    yt = YouTube(url)
    for n in range(6):
        try:
            description = yt.initial_data["engagementPanels"][n][
                "engagementPanelSectionListRenderer"]["content"][
                "structuredDescriptionContentRenderer"]["items"][1][
                "expandableVideoDescriptionBodyRenderer"][
                "attributedDescriptionBodyText"]["content"]
            return description
        except KeyError:
            continue
    return False

def download_audio(url):
    print("Downloading audio...")
    video = YouTube(url).streams.filter(only_audio=True).first().download()
    return video

def trim_file_to_size(filepath, max_size):
    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size} bytes")

    if file_size <= max_size:
        return filepath

    print(f"File size exceeds the maximum size of {max_size} bytes. Trimming the file...")
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

def transcribe(audio_filepath, language=None, response_format='text', prompt=None):
    # 파일 크기 제한 (25MB)
    # Maximum content size limit는 26214400이지만 여유를 두기 위해 26210000으로 설정
    MAX_FILE_SIZE = 26210000

    # 파일 크기를 확인하고 필요한 경우 자르기
    trimmed_audio_filepath = trim_file_to_size(audio_filepath, MAX_FILE_SIZE)

    # 받아쓰기
    print("Transcribing audio...")
    with open(trimmed_audio_filepath, "rb") as file:
        # 매개변수 딕셔너리 생성
        kwargs = {
            'file': file,
            'model': "whisper-1",
            'response_format': response_format
        }

        # language가 제공되면 딕셔너리에 추가
        if language is not None:
            kwargs['language'] = language

        # prompt가 제공되면 딕셔너리에 추가
        if prompt is not None:
            kwargs['prompt'] = prompt

        # 받아쓰기 요청
        transcript = openai_client.audio.transcriptions.create(**kwargs)

    # 결과 저장
    st.session_state.transcript = transcript

    # 임시 파일이 생성되었을 경우 삭제
    if trimmed_audio_filepath != audio_filepath:
        os.remove(trimmed_audio_filepath)

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
prompt = st.text_area(
    "What's the video about? (Optional)",
    value=st.session_state.get('video_info', ''),
    help=(
        "Provide a brief description of the video or include specific terms like "
        "unique names and key topics to enhance accuracy. This can include spelling "
        "out hard-to-distinguish proper nouns."
    )
)

# 언어 이름과 ISO-639-1 형식 코드를 매핑한 딕셔너리
language_mapping = {
    '한국어': 'ko',
    'English': 'en',
    '日本語': 'ja',
    '中文': 'zh',
    'Español': 'es',
    'Français': 'fr',
    'Deutsch': 'de'
}

# 사용자에게 영상의 언어를 선택적으로 입력하도록 함
video_language_name = st.selectbox(
    "Select Language of the Video (optional):", 
    ['', '한국어', 'English', '日本語', '中文', 'Español', 'Français', 'Deutsch']
)
st.session_state.video_language = language_mapping.get(video_language_name, '')
st.session_state.response_format = st.selectbox(
    "Select Output Format:", ('text', 'srt', 'vtt')
    )

# 세션 상태 초기화
if 'transcript' not in st.session_state:
    st.session_state.transcript = ""
if 'summary' not in st.session_state:
    st.session_state.summary = ""

if st.button("Transcribe Video"):
    if url:
        with st.spinner('Downloading and transcribing video... This may take a while.'):
            filename = download_audio(url)
            transcribe(
                filename,
                language=st.session_state.video_language,
                response_format=st.session_state.response_format,
                prompt=prompt
            )
            os.remove(filename)  # 다운로드한 파일 삭제
        st.success('Done! Subtitles have been generated.')
        print("Transcription completed.")
    else:
        st.error("Please enter a URL.")

# 자막이 있을 경우, 자막 필드를 항상 표시
if st.session_state.transcript:
    st.text_area("Subtitles:", value=st.session_state.transcript, height=300)

st.session_state.content_type = st.selectbox(
    "Select Content Type:", 
    ["Simple summary", "Detailed summary", "Essay", "Blog article", 
     "Translation", "Comment on Key Moments"]
)

st.session_state.content_language = st.selectbox(
    "Select Language of the Content:", 
    ['Korean', 'English', 'Japanese', 'Chinese', 'Spanish', 'French', 
     'German']
)


prompt = {
    "Simple summary": (
        "Write a simple piece of the transcript in {language}. Keep it concise "
        "and highlight only the key points. Avoid detailed explanations."
    ),
    "Detailed summary": (
        "Provide a detailed piece of the transcript in {language}, including key "
        "points, important details, and any relevant context. Ensure that all "
        "significant aspects are covered comprehensively."
    ),
    "Essay": (
        "Write an essay based on the transcript in {language}. Provide a thorough "
        "analysis, include relevant context, and explore the topic in depth."
    ),
    "Blog article": (
        "Write a blog article based on the transcript in {language}. Make it "
        "engaging and informative, suitable for a general audience. Include "
        "anecdotes or interesting points to keep the reader's attention."
    ),
    "Translation": (
        "Translate the transcript into {language} without any summarization or "
        "modification. Keep the translation accurate and true to the original "
        "text."
    ),
    "Comment on Key Moments": (
        "Write a comment on the key moments from the transcript in {language}. "
        "Mention the most important or interesting parts and share your thoughts "
        "on them."
    ),
    "Critical Review": (
        "Write a critical review of the transcript in {language}. Evaluate the content, "
        "discuss its strengths and weaknesses, and provide constructive criticism."
    )
}

def generate_content(content_type, content_language, transcript, client, model):
    messages = [
        {
            "role": "system",
            "content": prompt[content_type].format(language=content_language)
        },
        {
            "role": "user",
            "content": f"Transcript:\n{transcript}\n\n"
                       f"{content_type} in {content_language}:"
        },
    ]

    temperature = 0.5
    if content_type in ["Essay", "Blog article", "Comment on Key Moments"]:
        temperature = 0.8
    elif content_type in ["Simple Summary", "Detailed Summary", "Translation"]:
        temperature = 0.3

    print(f"Generating {content_type} in {content_language} using {model} with temperature {temperature} ...")
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
    )
    print("Content generated.")
    return response.choices[0].message.content


def extract_dialogues_from_srt(srt_content):
    lines = srt_content.strip().split('\n')
    # 2번째 인덱스부터 시작해서 매 4번째 줄마다 추출
    dialogues = [lines[i] for i in range(2, len(lines), 4)]
    return '\n'.join(dialogues)


if st.button("Generate Content"):
    if st.session_state.transcript:
        content_type = st.session_state.content_type
        content_language = st.session_state.content_language
        transcript_to_summarize = st.session_state.transcript
        
        # Extract dialogues from SRT format before summarizing
        if st.session_state['response_format'] == 'srt':
            transcript_to_summarize = extract_dialogues_from_srt(
                transcript_to_summarize
            )

        try:
            model = "gpt-3.5-turbo"
            if (st.session_state.video_language == "ko" and 
                st.session_state.content_language == "Korean" and
                content_type in ["Blog article"]):
                model = "solar-1-mini-chat"
            if content_type in ["Translation", "Comment on Key Moments"]:
                model = "gpt-4o"
            
            client = (upstage_client if model == "solar-1-mini-chat" 
                      else openai_client)

            # Generate summary
            st.session_state.summary = generate_content(
                content_type,
                content_language,
                transcript_to_summarize,
                client=client,
                model=model
            )
        except BadRequestError as e:
            # Retry with a different model on BadRequestError
            print("BadRequestError occurred: ", e)
            st.session_state.summary = generate_content(
                content_type,
                content_language,
                transcript_to_summarize,
                client=openai_client,
                model="gpt-4o"
            )


# 요약문이 있을 경우, 요약문 필드를 표시
if st.session_state.summary:
    st.text_area("Summary:", value=st.session_state.summary, height=150)
