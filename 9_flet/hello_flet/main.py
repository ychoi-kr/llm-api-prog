import flet as ft


def main(page: ft.Page):
    page.add(ft.SafeArea(ft.Text("안녕, Flet!")))


ft.app(main)
