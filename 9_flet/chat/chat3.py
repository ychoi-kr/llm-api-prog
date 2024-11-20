import flet as ft


class Message:
    def __init__(self, user, text, message_type):
        self.user = user
        self.text = text
        self.message_type = message_type

    def to_dict(self):
        return {"user": self.user, "text": self.text, "message_type": self.message_type}

    @staticmethod
    def from_dict(data):
        return Message(data["user"], data["text"], data["message_type"])


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
            # 로그인 메시지 전송
            login_message = Message(user=user_name_field.value, text=f"{user_name_field.value} 님이 입장했습니다.", message_type="login")
            page.pubsub.send_all(login_message.to_dict())
            page.update()

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
    def on_message(msg_dict):
        msg = Message.from_dict(msg_dict)
        if msg.message_type == "login":
            messages.controls.append(ft.Text(msg.text, italic=True, color=ft.colors.BLUE))
        elif msg.message_type == "chat":
            messages.controls.append(ft.Text(f"{msg.user}: {msg.text}"))
        page.update()

    # PubSub 구독
    page.pubsub.subscribe(on_message)

    # 메시지 전송 함수
    def send_click(e):
        user_name = page.session.get("user_name")
        if user_name:
            chat_message = Message(
                user=user_name, text=message_field.value, message_type="chat"
            )
            page.pubsub.send_all(chat_message.to_dict())
            message_field.value = ""
            page.update()
        else:
            dialog.open = True
            page.update()

    messages = ft.Column()
    message_field = ft.TextField(hint_text="입력한 메시지...", expand=True)
    send = ft.ElevatedButton("보내기", on_click=send_click)
    page.add(messages, ft.Row(controls=[message_field, send]))

ft.app(target=main)
