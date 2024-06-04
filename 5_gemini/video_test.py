from vertexai.generative_models import GenerativeModel, Part
import vertexai
   
vertexai.init(project="robotic-vista-415814", location="asia-northeast3")
model = GenerativeModel("gemini-1.5-flash-preview-0514")

prompt = """
비디오를 보고 다음 질문에 답하세요:
- 비디오에는 무엇이 나와 있나요?
- 비디오에서 어떤 행동이 일어나고 있나요?
- 이 비디오에 가장 적합한 태그 10개를 제시해 주세요.
"""
video = Part.from_uri(
    uri="gs://github-repo/img/gemini/multimodality_usecases_overview/photography.mp4",
    mime_type="video/mp4",
)

contents = [prompt, video]

response = model.generate_content(contents)
print(response.text.strip())

