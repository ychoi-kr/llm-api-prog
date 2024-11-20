import flet as ft

def main(page: ft.Page):
    page.title = "Flet Chat"

    # 사용자 이름 입력 다이얼로그 생성
    user_name_field = ft.TextField(label="이름을 입력하세요", autofocus=True)

    def join_click(e):
        if not user_name_field.value:
            user_name_field.error_text = "이름을 입력해 주세요!"
            user_name_field.update()
        else:
            page.session.set("user_name", user_name_field.value)
            dialog.open = False
            page.update()

    # 다이얼로그 UI 구성
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("어서오세요!"),
        content=ft.Column([user_name_field], tight=True),
        actions=[ft.ElevatedButton(text="입장", on_click=join_click)],
        actions_alignment="end",
    )
    page.overlay.append(dialog)
    dialog.open = True

    # 메시지 수신 함수
    def on_message(msg):
        messages.controls.append(ft.Text(msg))
        page.update()

    # PubSub 구독
    page.pubsub.subscribe(on_message)

    # 메시지 전송 함수
    def send_click(e):
        user_name = page.session.get("user_name")  # 사용자 이름 가져오기
        page.pubsub.send_all(f"{user_name}: {message_field.value}")
        message_field.value = ""
        page.update()

    messages = ft.Column()
    message_field = ft.TextField(hint_text="입력한 메시지...", expand=True)
    send = ft.ElevatedButton("보내기", on_click=send_click)
    page.add(messages, ft.Row(controls=[message_field, send]))

ft.app(target=main)
