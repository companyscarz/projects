import flet as ft
import requests


def signup_view(page, navigate):

    async def logic(e):
        try:
            response = requests.post("http://127.0.0.1:8080/signup",
                                     json={
                                         "username": enter_username.value,
                                         "email": enter_email.value,
                                         "password": enter_password.value
                                     })
            # res= response.json #convert the json to dictionary
            res = response.status_code
            data = response.json()

            if res == 200:

                # save the token on client storage then on session
                # get token
                token = data["token"]
                email = enter_email.value
                await page.shared_preferences.set("digital_read_user_token", token)
                # use this token for validation
                page.run_task(navigate, "/home")

            elif res == 400:
                message.visible = True
                message.value = "Fill in all fields, please!"

            elif res == 401:
                message.visible = True
                message.value = "Password must be at least 6 characters!"

            elif res == 403:
                message.visible = True
                message.value = "Email already registered!"

            elif res == 404:
                message.visible = True
                message.value = "An unexpected error occurred! \n Please try again."

            elif res == 405:
                message.visible = True
                message.value = "User name already in use!"

            else:
                message.visible = True
                message.value = "An unknown error occured!"

        except Exception as e:
            print(f"error on signup page: {e}")
            message.visible = True
            message.value = "Connection Error!"

    message = ft.Text("", size=15, color=ft.Colors.RED_900, visible=False)
    enter_username = ft.TextField(
        label="username", hint_text="username", autofocus=True)
    enter_email = ft.TextField(label="email", hint_text="email@mail.com")
    enter_password = ft.TextField(
        label="password", hint_text="password", password=True)

    signup_card = ft.Container(
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
                    "Create Account",
                    size=22,
                    weight=ft.FontWeight.BOLD
                ),
                ft.Text(
                    "Join Digital Read and start learning",
                    size=13,
                    color=ft.Colors.GREY_600
                ),

                message,

                enter_username,
                enter_email,
                enter_password,

                ft.ElevatedButton(
                    "Create Account",
                    width=300,
                    on_click=logic
                ),

                ft.TextButton(
                    "Already have an account? Log in",
                    on_click=lambda e: page.run_task(navigate, "/login")
                ),
            ]
        )
    )

    return ft.View(
        route="/signup",
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.GREY_100,
                content=signup_card
            )
        ]
    )
