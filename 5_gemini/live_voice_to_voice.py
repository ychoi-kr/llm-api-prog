import asyncio
import sounddevice as sd
import numpy as np
from google import genai
import os
from google.genai import types

MODEL = "gemini-2.0-flash-exp"
RATE = 24000
CHANNELS = 1
DTYPE = "int16"
RECORD_SECONDS = 5

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"), http_options={"api_version": "v1alpha"}
)
config = {
    "generation_config": {
        "response_modalities": ["AUDIO"],
        "temperature": 0.9,
        "candidate_count": 1,
    },
    "system_instruction": "당신은 한국어로 대화하는 AI 어시스턴트입니다.",
}


def play_audio(data: bytes):
    """모델 응답 오디오를 재생하는 함수."""
    audio_array = np.frombuffer(data, dtype=np.int16)
    sd.play(audio_array, samplerate=RATE)
    sd.wait()


async def read_audio_stream():
    """마이크 입력을 실시간으로 스트리밍"""
    chunk_duration = 0.5
    frames_per_chunk = int(RATE * chunk_duration)
    silence_threshold = 20  # 무음 임계값
    speech_threshold = 20  # 발화 시작 임계값
    silence_duration = 1.0  # 무음 지속 시간
    chunks_for_silence = int(silence_duration / chunk_duration)
    silent_chunks = 0
    speech_started = False

    print("마이크에 말씀해 주세요...")
    with sd.RawInputStream(
        samplerate=RATE, channels=CHANNELS, dtype=DTYPE, blocksize=frames_per_chunk
    ) as stream:
        try:
            while True:
                data, overflowed = stream.read(frames_per_chunk)
                if overflowed:
                    print("!", end="", flush=True)
                else:
                    print(".", end="", flush=True)

                # 음성 크기 계산 (RMS 값 사용)
                audio_data = np.frombuffer(bytes(data), dtype=np.int16)
                rms = np.sqrt(np.mean(np.square(audio_data)))

                # 발화 시작 감지
                if not speech_started and rms > speech_threshold:
                    # print("\n발화가 감지되었습니다. 계속 말씀해 주세요...")
                    speech_started = True
                    silent_chunks = 0  # 카운터 초기화

                # 발화가 시작된 후에만 무음 감지
                if speech_started:
                    if rms < silence_threshold:
                        silent_chunks += 1
                        if (
                            silent_chunks >= chunks_for_silence
                        ):  # {silence_duration}초 동안 무음이 감지되어 종료
                            break
                    else:
                        silent_chunks = max(0, silent_chunks - 1)  # 점진적 감소

                yield bytes(data)

        except KeyboardInterrupt:
            print("\n스트리밍 중지")


async def main():
    async with client.aio.live.connect(model=MODEL, config=config) as session:
        try:
            while True:  # 대화 세션 유지
                print("\n마이크에 말씀해주세요... (Ctrl+C로 중지)")

                # 실시간 마이크 입력 스트리밍
                last_chunk = None
                async for chunk in read_audio_stream():
                    if last_chunk is not None:
                        # 이전 청크는 end_of_turn=False로 전송
                        input_data = types.LiveClientRealtimeInput(
                            media_chunks=[
                                {"data": last_chunk, "mime_type": "audio/pcm"}
                            ]
                        )
                        await session.send(input_data, end_of_turn=False)
                    last_chunk = chunk

                if last_chunk is not None:
                    # 마지막 청크를 end_of_turn=True로 전송
                    input_data = types.LiveClientRealtimeInput(
                        media_chunks=[{"data": last_chunk, "mime_type": "audio/pcm"}]
                    )
                    await session.send(input_data, end_of_turn=True)

                    print("\n응답 수신 대기 중...")
                    response_chunks = []
                    async for response in session.receive():
                        if response.data is not None:
                            response_chunks.append(response.data)

                    if response_chunks:
                        print("응답 재생 중...")
                        complete_audio = b"".join(response_chunks)
                        play_audio(complete_audio)
                        print("\n계속 대화하시려면 말씀해주세요...")
        except KeyboardInterrupt:
            print("\n대화를 종료합니다.")
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            import traceback

            print(traceback.format_exc())
            raise e


if __name__ == "__main__":
    asyncio.run(main())
