import flet as ft
import requests
from datetime import time
from components.nav_bar import bottom_bar, top_bar
from components.content_card import open_payment_sheet


async def my_wallet(page, navigate):

    # get the token from client storage and pass them as headers
    client_token = await page.shared_preferences.get("digital_read_user_token")

    try:
        # make request to backend to get coins points and coins  of this specific user
        res = requests.get(
            "http://127.0.0.1:8080/wallet",
            headers={
                "token": client_token
            }
        )

        if res.status_code == 200:
            response = res.json()  # Convert JSON to Python dict
            coins = response.get("coins")  # get the user's coins
            points = response.get("points")  # get the user's points

            # this will handle the subscriptions and the coins and transactions
            my_wallet = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.TextButton(
                        "Back",
                        icon=ft.Icons.ARROW_BACK,
                        icon_color=ft.Colors.GREEN_600,
                        on_click=lambda e: page.run_task(navigate, "/account"),
                        expand=True
                    ),
                    ft.Text("My Wallet", size=30, weight=ft.FontWeight.BOLD,),
                    ft.Text("Choose a plan", size=22,
                            weight=ft.FontWeight.BOLD,),
                    ft.Row(
                        spacing=6,
                        align=ft.Alignment.CENTER,
                        controls=[
                            ft.Container(
                                padding=15,
                                expand=True,
                                bgcolor=ft.Colors.WHITE,
                                border_radius=16,
                                shadow=ft.BoxShadow(
                                    blur_radius=15,
                                    color=ft.Colors.BLACK12,
                                    offset=ft.Offset(0, 4)
                                ),
                                content=ft.Column(
                                    spacing=16,
                                    controls=[
                                        ft.Text(
                                            "Basic",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "$4.99",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Talk about basic plans",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        # call imported function "open_payment_sheet" from components to open bottomsheet and select payment method then make payments
                                        ft.Button("GRAB", color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_500, on_click=lambda e: open_payment_sheet(
                                            page, navigate, subscription_plan="BASIC", amount=400, action="SUBSCRIBE")),
                                    ]
                                )
                            ),
                            ft.Container(
                                padding=15,
                                expand=True,
                                bgcolor=ft.Colors.WHITE,
                                border_radius=16,
                                shadow=ft.BoxShadow(
                                    blur_radius=15,
                                    color=ft.Colors.BLACK12,
                                    offset=ft.Offset(0, 4)
                                ),
                                content=ft.Column(
                                    spacing=16,
                                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                                    controls=[
                                        ft.Text(
                                            "Standard",
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "$4.99",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Talk about basic plans",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        # call imported function "open_payment_sheet" from components to open bottomsheet and select payment method then make payments
                                        ft.Button("GRAB", color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_500, on_click=lambda e: open_payment_sheet(
                                            page, navigate, subscription_plan="STANDARD", amount=500, action="SUBSCRIBE")),
                                    ]
                                )
                            ),

                            ft.Container(
                                padding=15,
                                expand=True,
                                bgcolor=ft.Colors.WHITE,
                                border_radius=16,
                                shadow=ft.BoxShadow(
                                    blur_radius=15,
                                    color=ft.Colors.BLACK12,
                                    offset=ft.Offset(0, 4)
                                ),
                                content=ft.Column(
                                    spacing=16,
                                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                                    controls=[
                                        ft.Text(
                                            "Premium",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "$4.99",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Talk about basic plans",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        # call imported function "open_payment_sheet" from components to open bottomsheet and select payment method then make payments
                                        ft.Button("GRAB", color=ft.Colors.WHITE, bgcolor=ft.Colors.GREEN_500, on_click=lambda e: open_payment_sheet(
                                            page, navigate, subscription_plan="PREMIUM", amount=600, action="SUBSCRIBE")),
                                    ]
                                )
                            ),

                            ft.Divider(),
                        ]
                    ),

                    # this will show the persons current points, the converted coins and networth
                    ft.Container(
                        padding=15,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=16,
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            color=ft.Colors.BLACK12,
                            offset=ft.Offset(0, 4)
                        ),
                        content=ft.Row(
                            spacing=20,
                            expand=True,
                            scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                            auto_scroll=True,
                            controls=[
                                ft.Column(
                                    controls=[
                                        ft.Text("Your current points",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                ),
                                        ft.Text(
                                            f"{points}",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Remember this number keeps changing. \n ",
                                            size=12,
                                            width=300,
                                            color=ft.Colors.GREY_600,
                                        ),
                                        # show changing time after every 2 seconds
                                    ]
                                ),

                                ft.Divider(),

                                ft.Column(
                                    controls=[
                                        ft.Text("Your ScarZ coins",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                ),
                                        ft.Text(
                                            f"{coins}",
                                            size=15,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "The above figure keeps changing depending on the views, favourtites ad downloads you get on your content with subscription access. \n Tip for you: to gain more coins, people have to react to your conent which has subscrition access type",
                                            size=12,
                                            width=300,
                                            color=ft.Colors.GREY_600,
                                        ),
                                    ]
                                ),

                                ft.Divider(),

                                ft.Column(
                                    controls=[
                                        ft.Text("Withdraw Cash",
                                                size=20,
                                                weight=ft.FontWeight.BOLD,
                                                ),
                                        ft.Text(
                                            "Enter number of coins needed",
                                            size=15,
                                            weight=ft.FontWeight.NORMAL,
                                        ),
                                        ft.Row(
                                            spacing=5,
                                            controls=[ft. TextField(hint_text="Coins",
                                                                    border=ft.InputBorder.NONE, width=100,
                                                                    bgcolor=ft.Colors.BLUE_GREY_200,
                                                                    autofocus=True
                                                                    ),
                                                      ft.Button("Withdraw",
                                                                color=ft.Colors.WHITE,
                                                                bgcolor=ft.Colors.AMBER_900,
                                                                on_click=lambda e: open_payment_sheet(
                                                                    page, navigate, subscription_plan="PREMIUM", amount=600, action="WITHDRAW")
                                                                )]),
                                    ]
                                ),
                            ]
                        )
                    ),
                ]
            )

            return ft.View(
                route="/my_wallet",
                controls=[
                    top_bar(page, navigate),
                    ft.Container(
                        expand=True,
                        bgcolor=ft.Colors.GREY_100,
                        content=my_wallet,
                    ),
                ]
            )
        # when the status code returns something different
        elif res.status_code == 401 or not client_token:
            page.run_task(navigate, "/login")
            return

        else:
            my_wallet = ft.Column(
                spacing=10,
                scroll=ft.ScrollMode.ALWAYS,
                controls=[
                    ft.Text("Unkown Error", size=22, color=ft.Colors.RED_600),
                ]
            )

        return ft.View(
            route="/my_wallet",
            controls=[
                top_bar(page, navigate),
                ft.Container(
                    expand=True,
                    bgcolor=ft.Colors.GREY_100,
                    content=my_wallet,
                ),
            ]
        )

    except Exception as e:
        my_wallet = ft.Column(
            spacing=10,
            scroll=ft.ScrollMode.ALWAYS,
            controls=[
                ft.Text(f"Sever Error: {e}", size=22,
                        weight=ft.FontWeight.BOLD,),
            ]
        )

    return ft.View(
        route="/my_wallet",
        controls=[
            top_bar(page, navigate),
            ft.Container(
                expand=True,
                bgcolor=ft.Colors.GREY_100,
                content=my_wallet,
            ),
        ]
    )
