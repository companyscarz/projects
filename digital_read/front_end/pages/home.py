import flet as ft
import requests
from datetime import datetime
from components.nav_bar import bottom_bar, top_bar


async def home_view(page, navigate):

    # get the token from client storage and pass them as headers
    client_token = await page.shared_preferences.get("digital_read_user_token")

    try:
        res = requests.get(
            "http://127.0.0.1:8080/home",
            headers={
                "token": client_token
            }
        )

        if res.status_code == 200:
            response = res.json()  # get the data
            user = response.get("user_details", [])  # get user details
            details = ft.Container(
                alignment=ft.Alignment.CENTER,
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=20,
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[
                        # container for documents
                        # ft.Image(
                        #   src="https://picsum.photos/200/200?",
                        #    expand=True,
                        #    fit=ft.BoxFit.CONTAIN,
                        # ),

                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        f'Hello {user["username"]}!', size=25),
                                    ft.Text("Welcome To Digital Read!",
                                            weight=ft.FontWeight.BOLD, size=35),
                                    ft.Text(
                                        'Your gateway to endless knowlwedge awaits!'),
                                ]
                            ),
                        ),
                        ft.Row(
                            spacing=16,
                            scroll=ft.ScrollMode.AUTO,
                            auto_scroll=True,
                            controls=[
                                ft.Container(
                                    width=160,
                                    padding=15,
                                    border_radius=15,
                                    bgcolor=ft.Colors.BLUE_50,
                                    on_click=lambda e: page.run_task(
                                        navigate, "/documents"),
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.BOOK),
                                            ft.Text("Explore E-Books",
                                                    weight=ft.FontWeight.BOLD),
                                            ft.Divider(),
                                            ft.Text(
                                                "Browse our vast library.", size=12)
                                        ]
                                    )
                                ),
                                ft.Container(
                                    width=160,
                                    padding=15,
                                    border_radius=15,
                                    bgcolor=ft.Colors.GREY_100,
                                    on_click=lambda e: page.run_task(
                                        navigate, "/podcasts"),
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(ft.Icons.HEADPHONES),
                                            ft.Text("Explore Audio-Books",
                                                    weight=ft.FontWeight.BOLD),
                                            ft.Divider(),
                                            ft.Text(
                                                "Browse our vast Audio Book library.", size=12)
                                        ]
                                    )
                                ),
                                ft.Container(
                                    width=160,
                                    padding=15,
                                    border_radius=15,
                                    bgcolor=ft.Colors.GREEN_50,
                                    on_click=lambda e: page.run_task(
                                        navigate, "/videos"),
                                    content=ft.Column(
                                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.VIDEO_LIBRARY_OUTLINED),
                                            ft.Text("Explore Video",
                                                    weight=ft.FontWeight.BOLD),
                                            ft.Divider(),
                                            ft.Text(
                                                "Browse our various education videos.", size=12)
                                        ]
                                    )
                                ),
                            ]
                        ),
                        ft.Button("My Account", color=ft.Colors.WHITE, expand=True,
                                  bgcolor=ft.Colors.BLUE_500, on_click=lambda e: page.run_task(navigate, "/account"))
                    ]
                )
            )

            return ft.View(
                route="/home",
                controls=[
                    # top_bar(page, navigate,),
                    details,
                    # bottom_bar(page, navigate, active="home"),
                ]
            )

        elif res.status_code == 401 or not client_token:
            page.run_task(navigate, "/login")
            return None

        elif res.status_code == 500:
            details = ft.Container(
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[
                        # container for documents
                        ft.Container(
                            content=ft.Column(controls=[
                                ft.Row(
                                    controls=[ft.Text("Error 500", size=22, weight=ft.FontWeight.BOLD,),]),
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route="/home",
                controls=[
                    top_bar(page, navigate,),
                    details,
                    bottom_bar(page, navigate, active="home"),
                ]
            )

        else:
            details = ft.Container(
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[
                        # container for documents
                        ft.Container(
                            content=ft.Column(controls=[
                                ft.Text("Unkown Error", size=22,
                                        color=ft.Colors.RED_600),
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route="/home",
                controls=[
                    top_bar(page, navigate,),
                    details,
                    bottom_bar(page, navigate, active="home"),
                ]
            )

    except Exception as e:
        details = ft.Container(
            expand=True,
            border_radius=ft.BorderRadius.all(20),
            padding=20,
            content=ft.Column(
                scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                controls=[
                    # container for documents
                    ft.Container(
                        content=ft.Column(controls=[
                            ft.Text(
                                f"Sever Error: {e}", size=22, weight=ft.FontWeight.BOLD,),
                        ]),
                    ),
                ]
            )
        )

        return ft.View(
            route="/home",
            controls=[
                top_bar(page, navigate,),
                details,
                bottom_bar(page, navigate, active="home"),
            ]
        )
