from pytube import YouTube

url = "https://www.youtube.com/watch?v=i-E7NiyRDa0"
yt = YouTube(url)  # YouTube 객체 생성
stream = yt.streams.get_highest_resolution()  # 가장 높은 해상도의 스트림 선택

# 동영상 다운로드
file_path = stream.download(output_path="./videos")
print("Download complete!")
