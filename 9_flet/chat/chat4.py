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


class ChatMessage(ft.Row):
    def __init__(self, message):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(message.user)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(message.user),
            ),
            ft.Column(
                [
                    ft.Text(message.user, weight="bold"),
                    ft.Text(message.text, selectable=True),
                ],
                tight=True,
                spacing=5,
            ),
        ]

    def get_initials(self, user_name):
        return user_name[:1].upper()

    def get_avatar_color(self, user_name):
        colors_lookup = [
            ft.colors.AMBER,
            ft.colors.BLUE,
            ft.colors.BROWN,
            ft.colors.CYAN,
            ft.colors.GREEN,
            ft.colors.INDIGO,
            ft.colors.LIME,
            ft.colors.ORANGE,
            ft.colors.PINK,
            ft.colors.PURPLE,
            ft.colors.RED,
            ft.colors.TEAL,
            ft.colors.YELLOW,
        ]
        return colors_lookup[hash(user_name) % len(colors_lookup)]


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
            messages.controls.append(ChatMessage(msg))

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

    messages = ft.ListView(
        expand=True,
        spacing=10,
        auto_scroll=True,
    )
    message_field = ft.TextField(
        hint_text="메시지를 입력하세요...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
    )
    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        tooltip="메시지 보내기",
        on_click=send_click,
    )

    page.add(
        ft.Container(
            content=messages,
            border=ft.border.all(1, ft.colors.OUTLINE),
            border_radius=5,
            padding=10,
            expand=True,
        ),
        ft.Row(
            [message_field, send_button],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
    )


ft.app(target=main)
