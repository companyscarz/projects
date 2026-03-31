import flet as ft
import requests


def login_view(page, navigate):

    async def logic(e):
        try:
            response = requests.post(
                "http://127.0.0.1:8080/login",
                json={
                    "email": email.value,
                    "password": password.value
                }
            )

            if response.status_code == 200:
                data = response.json()
                await page.shared_preferences.set(
                    "digital_read_user_token", data["token"]
                )
                page.run_task(navigate, "/home")

            elif response.status_code in [401, 402]:
                message.visible = True
                message.value = "Invalid email or password."

            elif response.status_code == 400:
                message.visible = True
                message.value = "Please fill in all fields."

            else:
                message.visible = True
                message.value = "Something went wrong."

        except Exception as e:
            message.visible = True
            message.value = "Connection error."

    message = ft.Text("", color=ft.Colors.RED_700, visible=False)

    email = ft.TextField(
        label="Email",
        hint_text="email@mail.com",
        autofocus=True
    )

    password = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True
    )

    login_card = ft.Container(
        width=360,
        padding=24,
        bgcolor=ft.Colors.WHITE,
        border_radius=16,
        shadow=ft.BoxShadow(
            blur_radius=15,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 4)
        ),
        content=ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
            controls=[
                ft.Text(
                    "Welcome Back",
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Log into your Digital Read account",
                    size=13,
                    color=ft.Colors.GREY_600
                ),

                message,
                email,
                password,
                ft.ElevatedButton(
                    "Continue",
                    width=300,
                    on_click=logic
                ),

                ft.TextButton(
                    "Don't have an account? Sign up",
                    on_click=lambda e: page.run_task(navigate, "/signup")
                ),
            ]
        )
    )

    return ft.View(
        route="/login",
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.GREY_100,
                content=login_card
            )
        ]
    )
