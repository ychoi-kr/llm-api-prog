import flet as ft

def main(page: ft.Page):
    page.title = "Flet Chat"

    # 메시지 수신 함수
    def on_message(msg):
        messages.controls.append(ft.Text(msg))
        page.update()

    # PubSub 구독
    page.pubsub.subscribe(on_message)

    # 메시지 전송 함수
    def send_click(e):
        page.pubsub.send_all(f"{user.value}: {message_field.value}")
        # 입력 필드 초기화
        message_field.value = ""
        page.update()

    messages = ft.Column()
    user = ft.TextField(hint_text="이름", width=150)
    message_field = ft.TextField(hint_text="입력한 메시지...", expand=True)  # 공간 채우기
    send = ft.ElevatedButton("보내기", on_click=send_click)
    page.add(messages, ft.Row(controls=[user, message_field, send]))

ft.app(target=main)
