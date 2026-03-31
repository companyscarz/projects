import flet as ft
import requests
from components.nav_bar import bottom_bar, top_bar

def settings(page, navigate):
    def change_profile_logic(e):
        pass

    def terminate_logic(e):
        pass

    async def logic(e):
        try:
            response = requests.post(
                "http://127.0.0.1:8080/services",
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
                message.visible=True
                message.value = "Invalid email or password."

            elif response.status_code == 400:
                message.visible=True
                message.value = "Please fill in all fields."

            else:
                message.visible=True
                message.value = "Something went wrong."

        except Exception as e:
            message.visible=True
            message.value = "Connection error."


    message = ft.Text("", color=ft.Colors.RED_700, visible=False)

    profile_picture = ft.Image(
        src="https://picsum.photos/200/200?",
        width=100,
        height=100,
        border_radius=1,
    )
    change_picture=ft.TextButton("Change profile", icon=ft.Icons.EDIT)

    change_theme = ft.Switch(label="Light mode", value=True, expand=True, scale=0.9,)

    username = ft.TextField(
        label="username",
        value="current user name",
        autofocus=True
    )

    new_password = ft.TextField(
        label="New_Password",
        password=True,
        can_reveal_password=True
    )
    
    old_password = ft.TextField(
        label="old Password",
        password=True,
        can_reveal_password=True
    )
    terminate_button = ft.Button(
        "Terminate my account",
        bgcolor=ft.Colors.RED_600,
        color=ft.Colors.WHITE,
        expand=True
    )
    my_settings = ft.Container(
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
                    "Settings",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Don't forget to save your changes.",
                    size=13,
                    color=ft.Colors.GREY_600
                ),

                message,

                #section for app apearance
                profile_picture,
                change_picture,
                
                #section for app appearance
                ft.Row(
                    spacing=-6,
                    controls=[
                    ft.Text("Theme:", weight=ft.FontWeight.W_600), 
                    change_theme,
                    ]),

                #section for account actions
                username,
                new_password,
                old_password,

                #divide line
                ft.Divider(),

                #section for acction buttons
                ft.Row(
                    controls=[
                        ft.TextButton(
                            "Back",
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.GREEN_600,
                            on_click=lambda e: page.run_task(navigate, "/account"),
                            expand=True
                        ),

                        ft.ElevatedButton(
                            "Save",
                            icon=ft.Icons.SETTINGS,

                            on_click=logic,
                            expand=True
                        ),
                    ]
                ),
                terminate_button,
            ]
        )
    )

    return ft.View(
        route="/settings",
        controls=[
            top_bar(page, navigate),
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.GREY_100,
                content=my_settings,
            ), 
            bottom_bar(page, navigate, active="account")
        ]
    )
