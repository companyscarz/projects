import flet as ft

def Error_500(page):
    my_row = ft.ListView(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=8, padding=16, 
                            auto_scroll=False,)

    for i in range(0,10):
        my_row.controls.append(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Image(src=f"https://picsum.photos/200/200?{i}",
                                     width=150,
                                     height=190,
                                     fit="contain",
                                     border_radius=ft.border_radius.all(10),
                            ),
                            ft.Row(controls=[ft.Text("Error 500", size=30, weight=ft.FontWeight.BOLD,)]),
                            ft.Row(controls=[ft.Text("", size=25, weight=ft.FontWeight.BOLD,)]),
                        ]
                    ),
                ]
            )
        )
        
    return my_row

def Error_unkown(page):
    my_row = ft.ListView(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=8, padding=16, 
                            auto_scroll=False,)

    for i in range(0,10):
        my_row.controls.append(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Image(src=f"https://picsum.photos/200/200?{i}",
                                     width=150,
                                     height=190,
                                     fit="contain",
                                     border_radius=ft.border_radius.all(10),
                            ),
                            ft.Row(controls=[ft.Text("Unkown Error", size=30, weight=ft.FontWeight.BOLD,)]),
                            ft.Row(controls=[ft.Text("", size=25, weight=ft.FontWeight.BOLD,)]),
                        ]
                    ),
                ]
            )
        )
        
    return my_row


def Sever_Error(page):
    my_row = ft.ListView(expand=True, scroll=ft.ScrollMode.ALWAYS, spacing=8, padding=16, 
                            auto_scroll=False,)

    for i in range(0,10):
        my_row.controls.append(
            ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Image(src=f"https://picsum.photos/200/200?{i}",
                                     width=150,
                                     height=190,
                                     fit="contain",
                                     border_radius=ft.border_radius.all(10),
                            ),
                            ft.Row(controls=[ft.Text("Server Error", size=30, weight=ft.FontWeight.BOLD,)]),
                            ft.Row(controls=[ft.Text("", size=25, weight=ft.FontWeight.BOLD,)]),
                        ]
                    ),
                ]
            )
        )
        
    return my_row
