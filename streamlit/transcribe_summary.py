import re
import os
import time
import tempfile

import streamlit as st
from pytube import YouTube
from openai import OpenAI
from openai import BadRequestError
import tiktoken


# 클라이언트 초기화
openai_client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"]
)
upstage_client = OpenAI(
    api_key=st.secrets["UPSTAGE_API_KEY"],
    base_url="https://api.upstage.ai/v1/solar"
)


def extract_keywords(title, description):
    messages = [
        {
            "role": "system",
            "content": (
                "Split text into lines and tag each line with labels such as "
                "'title', 'video_description', 'channel_description', 'tags', "
                "'timestamps', 'promotion', 'links', 'etc' in XML format. "
                "And then, extract the keywords from the 'title' and "
                "'video_description' tags and include them in a single "
                "'<keywords>' tag as a comma-separated list."
            )
        },
        {
            "role": "user",
            "content": f"{title}\n\n{description}\n\n"
        }
    ]
    
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5
    )
    
    xml_content = response.choices[0].message.content
    print("XML content:", xml_content)

    # <keywords> 태그 안의 내용만 추출
    keywords = re.search(
        r'<keywords>(.*?)</keywords>',
        xml_content,
        re.DOTALL
    )
    
    if keywords:
        return keywords.group(1).strip()
    else:
        st.info("No keywords found in the content.")
        return ""


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
    max_retries = 3
    retry_delay = 5  # seconds

    for retry in range(max_retries):
        try:
            video = YouTube(url).streams.filter(only_audio=True).first().download()
            return video
        except Exception as e:
            print(f"Error occurred while downloading audio: {str(e)}")
            if retry < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds... (Attempt {retry + 1} of {max_retries})")
                time.sleep(retry_delay)
            else:
                print(f"Max retries reached. Unable to download audio.")
                raise

    return None


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
st.title("YouTube Transcription and Content Generation")

url = st.text_input("Enter Video URL:")

# 유튜브 영상 정보 가져오기 버튼
if st.button("Load Video Info"):
    if url:
        title, description = get_video_info(url)
        transcription_prompt = extract_keywords(title, description)
        st.session_state.video_info = transcription_prompt
    else:
        st.error("Please enter a valid YouTube URL.")

# 영상 정보를 프롬프트에 표시
prompt = st.text_area(
    "What's in the video? (Optional)",
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
     "Translation", "Comment on Key Moments", "Critical Review"]
)

st.session_state.content_language = st.selectbox(
    "Select Language of the Content:", 
    ['Korean', 'English', 'Japanese', 'Chinese', 'Spanish', 'French', 
     'German']
)


prompt = {
    "Simple summary": (
        "Write a simple summary in {language}. Keep it concise and highlight "
        "only the key points. Avoid detailed explanations."
    ),
    "Detailed summary": (
        "Provide a detailed summary in {language}, including key points, "
        "important details, and any relevant context. Ensure that all "
        "significant aspects are covered comprehensively."
    ),
    "Essay": (
        "Write an essay based on the content in {language}. Provide a thorough "
        "analysis, include relevant context, and explore the topic in depth."
    ),
    "Blog article": (
        "Write a blog article based on the content in {language}. Make it "
        "engaging and informative, suitable for a general audience. Include "
        "anecdotes or interesting points to keep the reader's attention."
    ),
    "Translation": (
        "Translate the content into {language} without any summarization or "
        "modification. Keep the translation accurate and true to the original "
        "text."
    ),
    "Comment on Key Moments": (
        "Write a comment on the key moments from the content in {language}. "
        "Mention the most important or interesting parts and share your "
        "thoughts on them."
    ),
    "Critical Review": (
        "Write a critical review of the content in {language}. Evaluate the "
        "content, discuss its strengths and weaknesses, and provide "
        "constructive criticism."
    )
}


def get_tokenizer(model_name):
    if model_name.startswith("gpt"):
        return tiktoken.encoding_for_model(model_name)
    else:
        # 정확하게 하려면 모델별 토큰화기를 달리해야 하지만 여기서는 간단하게 처리
        return tiktoken.encoding_for_model("gpt-3.5-turbo")


def split_into_chunks(text, max_tokens, tokenizer):
    print(f"Checking if transcript fits within the token limit of {max_tokens}...")
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = []
    current_chunk_tokens = 0

    for paragraph in paragraphs:
        paragraph_tokens = len(tokenizer.encode(paragraph))

        if current_chunk_tokens + paragraph_tokens <= max_tokens:
            current_chunk.append(paragraph)
            current_chunk_tokens += paragraph_tokens
        else:
            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))
            current_chunk = [paragraph]
            current_chunk_tokens = paragraph_tokens

    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))

    if len(chunks) > 1:
        print(f"Split transcript into {len(chunks)} chunks.")
    
    return chunks


def translate(source_text, source_language_code, target_language_name):
    print(f"Translating {source_language_code} text into {target_language_name} ...")
    
    content_type = "Translation"
    temperature = 0.4

    preferred_model = ""
    if source_language_code == "en" and target_language_name == "Korean":
        preferred_model = "solar-1-mini-translate-enko"
    elif source_language_code == "ko" and target_language_name == "English":
        preferred_model = "solar-1-mini-translate-koen"
    else:
        preferred_model = "gpt-3.5-turbo"
    
    fallback_model = "gpt-4-turbo"

    client = upstage_client if preferred_model.startswith("solar") else openai_client

    chunk_size = 1024  # 실험 결과에 따라 조정
    tokenizer = get_tokenizer("gpt-3.5-turbo")
    chunks = split_into_chunks(source_text, chunk_size, tokenizer)
    
    results = []
    progress_text = "Translation progress"
    my_bar = st.progress(0, text=progress_text)
    
    for i, chunk in enumerate(chunks, start=1):
        messages = []
        if preferred_model in ["solar-1-mini-translate-enko", 
                                "solar-1-mini-translate-koen"]:
            messages = [
                {
                    "role": "user",
                    "content": chunk
                }
            ]
        else:
            messages = [
                {
                    "role": "system",
                    "content": prompt[content_type].format(language=target_language_name)
                },
                {
                    "role": "user",
                    "content": (f"Transcript:\n{chunk}\n\n"
                                f"{content_type} in {target_language_name}:")
                }
            ]

        try:
            response = client.chat.completions.create(
                model=preferred_model,
                messages=messages,
                temperature=temperature
            )
        except BadRequestError as e:
            print("BadRequestError occurred: ", e)
            print(f"Retrying translation using {fallback_model} ...")
            response = client.chat.completions.create(
                model=fallback_model,
                messages=messages,
                temperature=temperature
            )
        finally:
            results.append(response.choices[0].message.content)
            progress = i / len(chunks)
            my_bar.progress(progress, text=f"{progress_text} {progress:.0%}")
    
    print("Translation completed.")
    return "\n".join(results)


def generate_content(content_type, content_language, transcript_language_code, transcript_format, transcript):
    
    if content_type == "Translation":
        return translate(transcript, transcript_language_code, content_language)
    
    tokenizer = get_tokenizer("gpt-3.5-turbo")
    num_tokens = len(tokenizer.encode(transcript))

    margin = 3000 if content_type in ["Detailed Summary", "Essay", "Blog article"] else 1000

    preferred_model = ""
    if num_tokens < 16385 - margin:
        preferred_model = "gpt-3.5-turbo"
    elif num_tokens < 32768 - margin:
        preferred_model = "solar-1-mini-chat"
    else:
        preferred_model = "gpt-4o"
    
    fallback_model = "gpt-4-turbo"

    temperature = 0.5
    if content_type in ["Essay", "Blog article", "Comment on Key Moments"]:
        temperature = 0.8
    elif content_type in ["Simple Summary", "Detailed Summary"]:
        temperature = 0.4

    if transcript_format == "srt":
        transcript = extract_dialogues_from_srt(transcript)
    
    print(f"Generating {content_type} in {content_language} with temperature {temperature} ...")
    
    messages = [
        {
            "role": "system",
            "content": prompt[content_type].format(language=content_language)
        },
        {
            "role": "user",
            "content": (f"Transcript:\n{transcript}\n\n"
                        f"{content_type} in {content_language}:")
        }
    ]
    
    result = ""
    try:
        print(f"Attempting to generate content using {preferred_model} ...")
        client = upstage_client if preferred_model.startswith("solar") else openai_client
        response = client.chat.completions.create(
            model=preferred_model,
            messages=messages,
            temperature=temperature
        )
        result = response.choices[0].message.content
    except BadRequestError as e:
        print("BadRequestError occurred: ", e)
        print(f"Retrying content generation using {fallback_model} ...")
        client = openai_client
        response = client.chat.completions.create(
            model=fallback_model,
            messages=messages,
            temperature=temperature
        )
        result = response.choices[0].message.content

    print("Content generated.")
    return result


def extract_dialogues_from_srt(srt_content):
    lines = srt_content.strip().split('\n')
    # 2번째 인덱스부터 시작해서 매 4번째 줄마다 추출
    dialogues = [lines[i] for i in range(2, len(lines), 4)]
    return '\n'.join(dialogues)


if st.button("Generate Content"):
    if st.session_state.transcript:
        content_type = st.session_state.content_type
        
        with st.spinner(f'\nGenerating {content_type}...'):
            generated_content = generate_content(
                content_type,
                st.session_state.content_language,
                st.session_state.video_language,
                st.session_state.response_format,
                st.session_state.transcript
            )
            st.session_state.summary = generated_content
        st.success('Content generation completed!')

# 요약문이 있을 경우, 요약문 필드를 표시
if st.session_state.summary:
    st.text_area("Summary:", value=st.session_state.summary, height=300)
