import flet as ft

def top_bar(page, navigate):

    search_field = ft.TextField(
        hint_text="Search",
        dense=True,
        border_radius=12,
        height=40,
        text_size=14,
        expand=True
    )

    return ft.Container(
        padding=ft.Padding(16, 12, 16, 12),
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            blur_radius=10,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 2),
        ),
        content=ft.Row(
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=12,
            controls=[
                ft.Text(
                    "Digital Read",
                    size=20,
                    weight=ft.FontWeight.BOLD
                ),

                ft.TextButton(
                    "Home",
                    icon=ft.Icons.HOME_FILLED,
                    on_click=lambda e: page.run_task(navigate, "/home")
                ),

                search_field,

                ft.IconButton(
                    icon=ft.Icons.SEARCH,
                    tooltip="Search"
                )
            ]
        )
    )



def bottom_bar(page, navigate, active: str = "home"):

    def nav_item(icon, route, key):
        is_active = active == key

        return ft.Container(
            width=48,
            height=48,
            border_radius=14,
            bgcolor=ft.Colors.BLUE_100 if is_active else None,
            content=ft.IconButton(
                icon=icon,
                icon_size=22,
                icon_color=ft.Colors.BLUE_700 if is_active else ft.Colors.GREY_600,
                on_click=lambda e: page.run_task(navigate, route),
            ),
        )

    return ft.Container(
        padding=ft.Padding(12, 8, 12, 8),
        margin=ft.Margin(12, 0, 12, 12),
        border_radius=24,
        bgcolor=ft.Colors.WHITE,
        shadow=ft.BoxShadow(
            blur_radius=20,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 6),
        ),
        content=ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_AROUND,
            controls=[
                nav_item(ft.Icons.PERSON_OUTLINE, "/account", "account"),
                nav_item(ft.Icons.DESCRIPTION_OUTLINED, "/documents", "documents"),
                nav_item(ft.Icons.HEADPHONES, "/podcasts", "podcasts"),
                nav_item(ft.Icons.VIDEO_LIBRARY_OUTLINED, "/videos", "videos"),
            ]
        )
    )
