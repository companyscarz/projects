import flet as ft
from flet_pdfview import PdfColumn
from flet import BoxFit
import webbrowser
import requests
from datetime import datetime
from components.nav_bar import top_bar, bottom_bar

# pass the page, navigate document(content)_id, user_id, username,


async def document_view(page, navigate, content_id, user_id, username):

    client_token = await page.shared_preferences.get("digital_read_user_token")
    content_type = "DOCUMENT"

    # function to make date into readble formart
    def format_datetime(dt_str):
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d %b %Y, %H:%M")

# ______________________------------------------------logic for dialogue----------------------------_________________________
    # function that deals with comment section dialog
    def open_comments_dialog(page, user_id, username, content_id):

        def close_dialog(e):  # function that closes the comment section dialog
            page.pop_dialog()

        def submit_comment(e):  # function that deals with submitting comments on a content
            if not comment_input.value.strip():  # if nothing is entered then do nothing
                return

            else:  # otherwise when field was filled
                # post the comment and related information to the server
                res = requests.post(
                    f"http://127.0.0.1:8080/comment_content",
                    json={
                        "token": client_token,
                        "content_type": content_type,
                        "comment": comment_input.value,
                        "user_id": user_id,
                        "content_id": content_id
                    }
                )

                if res.status_code == 200:  # if response is 200, everthing is ok, then add comment to the comment list and empty the comment field
                    comments_list.controls.append(
                        ft.Column(
                            spacing=-5,
                            expand=True,
                            controls=[
                                ft.Row(controls=[
                                    ft.Icon(ft.Icons.PERSON_2_ROUNDED),
                                    ft.Text(
                                        username, weight=ft.FontWeight.W_600),
                                ]),
                                ft.Text("posted on: time",
                                        color=ft.Colors.GREY_600),
                                ft.Text(comment_input.value)
                            ])
                    )
                    # add + 1 on comment
                    comments_count.value = int(comments_count.value) + 1
                else:  # if response is otherwise alert message
                    comment_message.visible = True
                    comment_message.value = "Failed to comment on posts!"
            comment_input.value = ""
            # page.update()

        # variable to hold comment entered
        comment_message = ft.Text("", color=ft.Colors.RED_600, visible=False)

        # list of comments from database and the recently added ones
        comments_list = ft.ListView(
            expand=True,
            spacing=8,
            height=300,
            auto_scroll=True,
            # GET COMMENTS FROM DATABASE IN DESCESNDING ORDER
            # ADD DELETE ICON TO DELETE, COMMENT IF ID MATCHES FOR USER
        )

        # entry field where comments are entered
        comment_input = ft.TextField(
            hint_text="Write a comment...",
            multiline=True,
            min_lines=2,
            max_lines=4,
            autofocus=True,
        )

        # the control for alert dialog
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Comments"),
            content=ft.Column(
                spacing=12,
                controls=[
                    comments_list,
                    comment_input,
                    comment_message
                ],
            ),
            actions=[
                ft.TextButton("Close", on_click=close_dialog),
                ft.Button("Send", on_click=submit_comment),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        # it calls the dialog to open when called
        page.show_dialog(dialog)

        # make request to backend to get comments of this specific document
        res = requests.get(
            f"http://127.0.0.1:8080/get_comments/{content_type}/{content_id}",
            headers={
                "token": client_token
            }
        )
        response = res.json()  # Convert JSON to Python dict
        document_comments = response.get(
            "document_comments", [])  # get documents data

        # if response is 200, everything is ok.. continue
        if res.status_code == 200:
            for comments in document_comments:
                # convert time of comment to readable format
                readable_time = format_datetime(comments['created_at'])
                comments_list.controls.append(  # added the got comment to the comment list
                    ft.Column(
                        spacing=-5,
                        expand=True,
                        controls=[
                            ft.Row(controls=[
                                # posters profile picture
                                ft.Icon(ft.Icons.PERSON_2_ROUNDED),
                                ft.Text(username, weight=ft.FontWeight.W_600),
                            ]),
                            ft.Text(
                                f"posted on: {readable_time}", color=ft.Colors.GREY_600),
                            ft.Text(comments["comments"])
                        ])
                )
        # else show alert message, failed to get comments
        else:
            comment_message.visible = True
            comment_message.value = "Failed to get comments!"

    # _________________________--------------------logic for sction buttons-------------------------_________________________________

    def handle_document_action(e, action, page, navigate):
        # when comment section is clicked then open a dialogue box having comments on the content and a field box allowing one who subscribed to comment
        if action == "COMMENT":
            open_comments_dialog(page, user_id=str(
                user_id), username=username, content_id=content_id)
            # page.run_task(navigate, f"/document/{info['id']}/comments")
            # open dialogue it shows all the comments by other pipo
            # allows one to add comment if not yet subscribe then redirect to subscribe page or just flash message
            # this will help in alogarithm to know what user likes

        elif action == "FAVORITE":
            # do nothing.. when in view mode activate it for one to like and unlike
            try:
                # request make a like
                response = requests.post(
                    "http://127.0.0.1:8080/like_content",
                    json={
                        "token": client_token,
                        "content_type": "DOCUMENT",
                        "content_id": f"{content_id}",
                        "user_id": f"{user_id}"
                    }
                )
                if response.status_code == 200:
                    # turn the like button dark red and add one to the likes counts
                    likes_count.value = int(likes_count.value) + 1
                    like_icon.icon_color = ft.Colors.RED_600
                    return None

                elif response.status_code == 203:
                    # turn the like button light red and subtract one from likes counts
                    likes_count.value = int(likes_count.value) - 1
                    like_icon.icon_color = ft.Colors.RED_300
                    return None

                elif response.status_code == 401:
                    message.color = ft.Colors.RED_600
                    message.value = "Invalid or expired token"
                    page.run_task(navigate, "/login")

                elif response.status_code == 500:
                    message.color = ft.Colors.RED_600
                    message.value = "Internal server error"

            except Exception as e:
                pass

            print(f"Favorited document {content_id}")
            message.visible = True
            message.color = ft.Colors.GREEN_600
            message.value = f"Favorited document"
            # adds a row to likes table in database, then gets them to get the number
            # if user already liked document then delete the row of id matching content, and user id matching
            # get count and update
            # this will help in alogarithm to know what user likes

        # will create a sqlite db to store saved data and deletes automaticallly after a period of time

        elif action == "DOWNLOAD":
            # do nothing.. when in view mode activate it for one to like and unlike
            try:
                # request make a like
                response = requests.post(
                    "http://127.0.0.1:8080/download_content",
                    json={
                        "token": client_token,
                        "content_type": content_type,
                        "content_id": content_id,
                        "user_id": user_id
                    }
                )
                if response.status_code == 200:
                    message.visible = True
                    message.color = ft.Colors.BLUE_600
                    message.value = f"Video Downloaded"

                elif response.status_code == 401:
                    message.color = ft.Colors.RED_600
                    message.value = "Invalid or expired token"
                    page.run_task(navigate, "/login")

                elif response.status_code == 402:
                    message.visible = True
                    message.color = ft.Colors.BLUE_600
                    message.value = "Downloaded again"
                    # create a database in user account to store bytes of content AND DELETE after a period of time

                elif response.status_code == 500:
                    message.color = ft.Colors.RED_600
                    message.value = "Internal server error"

            except Exception as e:
                pass
            # adds a row to downloads table in database, then gets them to get the number
            # this will help in alogarithm to know what user likes
            # get count and update

        elif action == "VIEW":
            # do nothing.. when in view mode activate it for one to like and unlike
            try:
                # request make a like
                response = requests.post(
                    "http://127.0.0.1:8080/view_content",
                    json={
                        "token": client_token,
                        "content_type": content_type,
                        "content_id": content_id,
                        "user_id": user_id
                    }
                )
                if response.status_code == 200:
                    # message.visible = True
                    # message.color = ft.Colors.BLUE_600
                    # message.value = f"Podcast VIEWED"
                    return None

                elif response.status_code == 401:
                    message.color = ft.Colors.RED_600
                    message.value = "Invalid or expired token"
                    page.run_task(navigate, "/login")
                    return None

                elif response.status_code == 402:
                    # message.visible = True
                    # message.color = ft.Colors.BLUE_600
                    # message.value = "PODCAST viewed again"
                    return None

                elif response.status_code == 500:
                    message.color = ft.Colors.RED_600
                    message.value = "Internal server error"
                    return None

            except Exception as e:
                pass

    try:
        res = requests.get(
            f"http://127.0.0.1:8080/one_content/{content_id}/{content_type}",
            headers={
                "token": client_token
            }
        )

        if res.status_code == 200:
            message = ft.Text("", visible=False)  # flashed messages variable
            response = res.json()  # Convert JSON to Python dict
            document_info = response.get(
                "documents", [])  # get documents data
            # get the temporary token to give access to view document
            temp_token = response.get("temp_token")
            email = document_info.get("email")

            # open document in the browser
            doc_web_res = requests.get(f"http://127.0.0.1:8080/web_pdf_viewer/{content_id}/{temp_token}/{email}",
                                       headers={
                                           "token": client_token
                                       })
            if doc_web_res.status_code == 200:
                webbrowser.open(
                    f"http://127.0.0.1:8080/web_pdf_viewer/{content_id}/{temp_token}/{email}")
            else:
                message = ft.Text("", visible=True)
                message.Value = "Failed to open Document"
                return None

            details = ft.Container(
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[
                        # container for documents should contain the document and a buttin that when clicked shows the reaction options
                        ft.Container(
                            content=ft.Column(controls=[
                                ft.Text("full Summary of the document"),
                                ft.Row(
                                    spacing=16,
                                    controls=[
                                        ft.Row(spacing=-4,
                                               controls=[
                                                   ft.IconButton(icon=ft.Icons.COMMENT_OUTLINED,
                                                                 tooltip="comments",
                                                                 on_click=lambda e: handle_document_action(e, "COMMENT", page, navigate)),  # opens function that opens a dialogue
                                                   comments_count := ft.Text(document_info.get(
                                                       "comments_count", 0), size=12),
                                               ]
                                               ),
                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.REMOVE_RED_EYE, size=16, color=ft.Colors.BLUE_GREY_600),
                                                # number of viewers
                                                ft.Text(document_info.get(
                                                    "views_count", 0), size=12)
                                            ]
                                        ),
                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                like_icon := ft.IconButton(icon=ft.Icons.FAVORITE, icon_size=16,
                                                                           # DISABLED IF NOT SUBSCRIBED
                                                                           icon_color=ft.Colors.RED,
                                                                           # call function that deals with like logic
                                                                           on_click=lambda e: handle_document_action(
                                                                               e, "FAVORITE", page, navigate)
                                                                           ),
                                                likes_count := ft.Text(document_info.get(
                                                    "likes_count", 0), size=12),
                                            ]
                                        ),
                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=16,
                                                              icon_color=ft.Colors.BLUE_600,
                                                              # call function that deals with download logic
                                                              on_click=lambda e: handle_document_action(
                                                                  e, "DOWNLOAD", page, navigate)
                                                              ),
                                                ft.Text(document_info.get(
                                                    "downloads_count", 0), size=12),
                                            ]
                                        ),
                                    ]
                                ),
                                message,
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route=f"/document_view/{content_id}",
                controls=[
                    top_bar(page, navigate,),  # topbar for digital_read
                    details,
                    # bottom nav bar
                    bottom_bar(page, navigate, active="documents"),
                ]
            )

        elif res.status_code == 401:
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
                                ft.Text(f"Error!", size=22,
                                        weight=ft.FontWeight.BOLD,),
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route=f"/document_view/{content_id}",
                controls=[
                    top_bar(page, navigate,),  # topbar for digital_read
                    details,
                    # bottom nav bar
                    bottom_bar(page, navigate, active="documents"),
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
                                ft.Text(f"Unkown Error!", size=22,
                                        weight=ft.FontWeight.BOLD,),
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route=f"/document_view/{content_id}",
                controls=[
                    top_bar(page, navigate,),  # topbar for digital_read
                    details,
                    # bottom nav bar
                    bottom_bar(page, navigate, active="documents"),
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
            route=f"/document_view/{content_id}",
            controls=[
                top_bar(page, navigate,),  # topbar for digital_read
                details,
                # bottom nav bar
                bottom_bar(page, navigate, active="documents"),
            ]
        )
