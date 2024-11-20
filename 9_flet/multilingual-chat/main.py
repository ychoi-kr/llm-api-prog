import flet as ft
import os
from openai import OpenAI
from pydantic import BaseModel

# OpenAI API 키 설정
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 메시지 클래스 정의
class Message:
    def __init__(self, user, text, message_type, translations=None):
        self.user = user
        self.text = text
        self.message_type = message_type
        self.translations = translations or {}

    def to_dict(self):
        return {
            "user": self.user,
            "text": self.text,
            "message_type": self.message_type,
            "translations": self.translations,
        }

    @staticmethod
    def from_dict(data):
        return Message(
            data["user"],
            data["text"],
            data["message_type"],
            data.get("translations", {}),
        )


# 채팅 메시지를 표시하는 클래스 정의 (자기 자신의 메시지)
class ChatMessage(ft.Row):
    def __init__(self, user_name, display_text):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(user_name),
            ),
            ft.Column(
                [
                    ft.Text(user_name, weight="bold"),
                    ft.Text(display_text, selectable=True),
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


# 다른 사용자의 메시지를 표시하는 클래스 정의 (원문과 번역문 모두 표시)
class ChatMessageWithTranslation(ft.Row):
    def __init__(self, user_name, original_text, translated_text):
        super().__init__()
        self.vertical_alignment = ft.CrossAxisAlignment.START
        self.controls = [
            ft.CircleAvatar(
                content=ft.Text(self.get_initials(user_name)),
                color=ft.colors.WHITE,
                bgcolor=self.get_avatar_color(user_name),
            ),
            ft.Column(
                [
                    ft.Text(user_name, weight="bold"),
                    ft.Text(f"Original: {original_text}", selectable=True),
                    ft.Text(f"Translated: {translated_text}", selectable=True),
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
    

# 번역 결과를 위한 Pydantic 모델 정의
class TranslationResponse(BaseModel):
    translation: str


def main(page: ft.Page):
    page.title = "Multilingual Chat"

    # 세션별 대화 내역 저장을 위한 딕셔너리
    if not hasattr(page.session, "conversation_history"):
        page.session.set("conversation_history", [])

    user_name_field = ft.TextField(label="Enter your name", autofocus=True)
    user_language_dropdown = ft.Dropdown(
        options=[
            ft.dropdown.Option("en", "English"),
            ft.dropdown.Option("ko", "한국어"),
            ft.dropdown.Option("ja", "日本語"),
        ],
        label="Select your language",
    )

    def join_click(e):
        if not user_name_field.value:
            user_name_field.error_text = "Name cannot be blank!"
            user_name_field.update()
        elif not user_language_dropdown.value:
            user_language_dropdown.error_text = "Please select a language!"
            user_language_dropdown.update()
        else:
            page.session.set("user_name", user_name_field.value)
            page.session.set("user_language", user_language_dropdown.value)
            dialog.open = False
            # 로그인 메시지 전송
            login_message = Message(
                user=user_name_field.value,
                text=f"{user_name_field.value} has joined the chat.",
                message_type="login"
            )
            page.pubsub.send_all(login_message.to_dict())
            page.update()

    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Welcome!"),
        content=ft.Column([user_name_field, user_language_dropdown], tight=True),
        actions=[ft.ElevatedButton(text="Join chat", on_click=join_click)],
        actions_alignment="end",
    )
    page.overlay.append(dialog)
    dialog.open = True

    def on_message(msg_dict):
        msg = Message.from_dict(msg_dict)
        current_user = page.session.get("user_name")
        user_language = page.session.get("user_language")

        # 세션별 대화 내역에 메시지 추가
        conversation_history = page.session.get("conversation_history")
        conversation_history.append(msg)
        page.session.set("conversation_history", conversation_history)

        if msg.message_type == "login":
            messages.controls.append(
                ft.Text(msg.text, italic=True, color=ft.colors.BLUE)
            )
        elif msg.message_type == "chat":
            if msg.user == current_user:
                # 자기 자신의 메시지는 원문만 표시
                messages.controls.append(ChatMessage(msg.user, msg.text))
                display_text = msg.text
            else:
                # 다른 사용자의 메시지는 원문과 번역문을 함께 표시
                original_text = msg.text
                translated_text = msg.translations.get(user_language, msg.text)
                messages.controls.append(
                    ChatMessageWithTranslation(msg.user, original_text, translated_text))
        page.update()

    page.pubsub.subscribe(on_message)

    def translate_text(text, target_language, conversation_history):
        # OpenAI API 호출 (동기 함수 사용)
        # 대화 맥락을 포함한 메시지 구성

        # 시작 부분에 'system' 메시지로 지시사항 추가
        messages_for_translation = [
            {
                "role": "system",
                "content": f"You are a helpful assistant that translates messages into {target_language}. "
                        "Consider the conversation context when translating the last message. "
                        "Provide only the translation in the 'translation' field of the JSON response."
            }
        ]
        
        # 최근 N개의 메시지 사용 (예: 5개)
        N = 5
        recent_history = conversation_history[-N:]

        for msg in recent_history:
            role = "assistant" if msg.user == page.session.get("user_name") else "user"
            messages_for_translation.append({"role": role, "content": msg.text})

        # 번역 요청 메시지 추가
        messages_for_translation.append(
            {
                "role": "user",
                "content": f"Please translate the last message to {target_language} considering the conversation context."
            }
        )

        completion = client.beta.chat.completions.parse(
            model="gpt-4o-2024-08-06",
            messages=messages_for_translation,
            response_format=TranslationResponse,
        )

        translation_response = completion.choices[0].message.parsed
        return translation_response.translation.strip()

    def send_click(e):
        user_name = page.session.get("user_name")
        user_language = page.session.get("user_language")
        if user_name:
            original_text = message_field.value.strip()
            if original_text:
                # 세션별 대화 내역 가져오기
                conversation_history = page.session.get("conversation_history")
                # 자기 자신의 메시지를 대화 내역에 추가
                my_message = Message(
                    user=user_name,
                    text=original_text,
                    message_type="chat",
                )
                conversation_history.append(my_message)
                page.session.set("conversation_history", conversation_history)

                target_languages = ["en", "ko", "ja"]
                translations = {}
                for lang in target_languages:
                    if lang != user_language:
                        try:
                            translated_text = translate_text(
                                original_text, lang, conversation_history
                            )
                            translations[lang] = translated_text
                        except Exception as ex:
                            print(f"Translation error: {ex}")
                            translations[lang] = original_text
                    else:
                        # 자기 자신의 언어는 번역하지 않음
                        continue

                chat_message = Message(
                    user=user_name,
                    text=original_text,
                    message_type="chat",
                    translations=translations,
                )
                page.pubsub.send_all(chat_message.to_dict())
                message_field.value = ""
                message_field.update()
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
        hint_text="Write a message...",
        autofocus=True,
        shift_enter=True,
        min_lines=1,
        max_lines=5,
        filled=True,
        expand=True,
        on_submit=send_click,
    )
    send_button = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        tooltip="Send message",
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


ft.app(target=main, view=ft.AppView.WEB_BROWSER)
