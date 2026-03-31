import flet as ft
import requests
from datetime import datetime
from components.nav_bar import bottom_bar, top_bar


async def account(page, navigate):

    # get the token from client storage and pass them as headers
    client_token = await page.shared_preferences.get("digital_read_user_token")

    # function that clears the client storage then pushes user to login page
    async def log_out(e):
        # delete the token rlated to this login
        await page.shared_preferences.clear()
        page.run_task(navigate, "/login")

    # function to make date into readble formart
    def format_datetime(dt_str):
        dt = datetime.fromisoformat(dt_str)
        return dt.strftime("%d %b %Y, %H:%M")

    def confirm_delete_post(page, content_type, content_id):

        def close_dlg(e):
            e.control.page.pop_dialog()

        def delete_task(e):
            # call request to delete post after close the dialogue
            # make a delete request
            response = requests.post(
                "http://127.0.0.1:8080/delete_content",
                json={
                    "token": client_token,
                    "content_type": content_type,
                    "content_id": content_id
                }
            )

            if response.status_code == 200:
                close_dlg(e)
                message.visible = True
                message.color = ft.Colors.GREEN_600
                message.value = "Post deleted"
                page.run_task(navigate, "/documents")

            elif response.status_code == 401:
                close_dlg(e)
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Invalid or expired token"
                page.run_task(navigate, "/login")

            else:
                close_dlg(e)
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Post failed to delete"

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("Please confirm"),
            content=ft.Text("Do you really want to delete this post?"),
            actions=[
                ft.TextButton("Yes", on_click=delete_task),
                ft.TextButton("No", on_click=close_dlg),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            # on_dismiss=lambda e: print("delete canceled"),
        )

        page.show_dialog(dlg_modal)  # show the dialog ti confirm post deleting


# ______________________------------------------------logic for dialogue----------------------------_________________________

    # function that deals with comment section dialog

    def open_comments_dialog(page, user_id, username, content_id, content_type):

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
                        "content_id": content_id,
                        "username": username
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
        get_comments = response.get("get_comments", [])  # get documents data

        # if response is 200, everything is ok.. continue
        if res.status_code == 200:
            for comments in get_comments:
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
                                ft.Text(comments['username'],
                                        weight=ft.FontWeight.W_600),
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

    def access_action_button(info, page, navigate, media_view):
        # if access_type for the document is free then access button is changed and color to show that is free to continue to read,
        # when clicked go to the document_view page passing media id there
        if info["access_type"] == "free":
            return ft.IconButton(
                icon=ft.Icons.PLAY_LESSON_ROUNDED,
                icon_size=17,
                icon_color=ft.Colors.GREEN_600,
                tooltip="free access",
                on_click=lambda e: page.run_task(
                    # route_name,document(content)_id, user_id, username,
                    navigate, f"/{media_view}/{info['id']}/{user['id']}/{user['username']}"
                )
            )
        else:
            # if paid content change icons respectively
            # in future check if user_id is in subsribtion table then allow access if not there deny
            return ft.IconButton(
                icon=ft.Icons.PLAY_LESSON_ROUNDED,
                icon_size=17,
                icon_color=ft.Colors.AMBER_900,
                tooltip="paid access",
                on_click=lambda e: page.run_task(
                    # route_name,document(content)_id, user_id, username,
                    navigate, f"/document_view/{info['id']}/{user['id']}/{user['username']}"
                )
            )


# _________________________--------------------logic for sction buttons-------------------------_________________________________

    def handle_document_action(e, action, info, page, navigate, content_type):
        # when comment section is clicked then open a dialogue box having comments on the content and a field box allowing one who subscribed to comment
        if action == "COMMENT":
            open_comments_dialog(page, user_id=str(
                user["id"]), username=user["username"], content_id=info["id"], content_type=content_type)
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
                        "content_id": f"{info['id']}",
                        "user_id": f"{info['id']}"
                    }
                )
                if response.status_code == 200:
                    pass

                elif response.status_code == 401:
                    message.color = ft.Colors.RED_600
                    message.value = "Invalid or expired token"
                    page.run_task(navigate, "/login")

                elif response.status_code == 500:
                    message.color = ft.Colors.RED_600
                    message.value = "Internal server error"

            except Exception as e:
                pass

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
                        "content_id": f"{info['id']}",
                        "user_id": f"{info['id']}"
                    }
                )

                if response.status_code == 200:
                    message.visible = True
                    message.color = ft.Colors.BLUE_600
                    message.value = f"Document Downloaded"

                elif response.status_code == 401:
                    message.visible = True
                    message.color = ft.Colors.RED_600
                    message.value = "Invalid or expired token"
                    page.run_task(navigate, "/login")

                elif response.status_code == 402:
                    message.visible = True
                    message.color = ft.Colors.BLUE_600
                    message.value = "Downloaded again"
                    # create a database in user account to store bytes of content AND DELETE after a period of time

                elif response.status_code == 500:
                    message.visible = True
                    message.color = ft.Colors.RED_600
                    message.value = "Internal server error"

            except Exception as e:
                pass
            # adds a row to downloads table in database, then gets them to get the number
            # this will help in alogarithm to know what user likes
            # get count and update

        elif action == "DELETE_POST":
            # call a function with a dialogue for deleting post
            content_id = info['id']
            confirm_delete_post(page, content_type, content_id)

        elif action == "EDIT":  # called when one wants to make edit to the selected media
            content_id = content_id = info["id"]
            title = info['title']
            theme = info['theme']
            level = info['level']
            description = info['description']
            access_type = info['access_type']
            cover_path = info["cover_path"]
            # route_name, content_id, user_id, username,..
            page.run_task(
                navigate, f"/edit_content/{content_id}/{title}/{theme}/{level}/{description}/{access_type}/{cover_path}/{content_type}")
            # passes relevant content to edit page for edit to be done

    try:
        # get token from client storage and pass them as headers
        res = requests.get(
            f"http://127.0.0.1:8080/my_content",
            headers={
                "token": client_token
            }
        )

        if res.status_code == 200:
            response = res.json()  # Convert JSON to Python dict

            documents = response.get("documents", [])  # get documents data
            podcasts = response.get("podcasts", [])  # get user podcasts data
            videos = response.get("videos", [])  # get user videos data
            user = response.get("user_details", [])  # get user details

            # row to hold the returned data
            my_document_list = ft.Row(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                auto_scroll=True,
                controls=[]
            )
            # loop through the returned data and show it inform of cards in the data_lst variable

            # beginning of for loop for documents
            for info in documents:
                # check if document is free so that one has full accesss to free ones otherwise no access
                is_free = info.get("access_type") == "free"

                # inlude for subscription if person in subscribed table then allow access if not deny access

                # append the content in form of cards to the my_document_list
                my_document_list.controls.append(
                    ft.Container(
                        padding=24,
                        width=350,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=16,
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            color=ft.Colors.BLACK_12,
                            offset=ft.Offset(0, 4)
                        ),
                        content=ft.Row(
                            controls=[
                                ft.Image(
                                    src=info.get(
                                        "cover_url", f'https://picsum.photos/200/200?'),  # image
                                    width=150,
                                    height=190,
                                    fit="contain",
                                    border_radius=ft.border_radius.all(10),
                                ),

                                ft.Column(
                                    expand=True,
                                    spacing=6,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(
                                                    info["title"],  # title
                                                    size=16,
                                                    expand=True,
                                                    weight=ft.FontWeight.BOLD,
                                                    max_lines=2,
                                                    overflow=ft.TextOverflow.ELLIPSIS
                                                ),
                                                ft.Row(spacing=-4,
                                                       controls=[
                                                           ft.IconButton(icon=ft.Icons.DELETE_FOREVER,
                                                                         icon_size=17,
                                                                         icon_color=ft.Colors.RED,
                                                                         tooltip="delete",
                                                                         on_click=lambda e, i=info, content_type="DOCUMENT": handle_document_action(e, "DELETE_POST", i, page, navigate, content_type,)),  # opens function that opens a dialogue to confirm post deleting
                                                       ]
                                                       ),
                                            ]
                                        ),

                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.PERSON_OUTLINE, size=16),
                                                ft.Text(
                                                    # authur
                                                    info.get(
                                                        "authur", "Unknown"),
                                                    size=12,
                                                    color=ft.Colors.BLUE_GREY_400
                                                ),
                                            ]
                                        ),

                                        ft.Text(
                                            # published date, call format_datetime() function to make date readable
                                            f'Published: {format_datetime(info.get("created_at", "N/A"))}',
                                            size=12,
                                            color=ft.Colors.BLUE_GREY_400
                                        ),

                                        ft.Text(
                                            # description if none show ....
                                            info.get("description", "..."),
                                            size=14,
                                            max_lines=3,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),

                                        ft.Row(
                                            spacing=3,
                                            controls=[
                                                ft.Row(spacing=-5,
                                                       controls=[
                                                           ft.IconButton(icon=ft.Icons.COMMENT_OUTLINED, icon_size=16,
                                                                         tooltip="comments",
                                                                         on_click=lambda e, i=info, content_type="DOCUMENT": handle_document_action(e, "COMMENT", i, page, navigate, content_type,)),  # opens function that opens a dialogue
                                                           ft.Text(
                                                               info.get("comments_count", 0), size=12),
                                                       ]
                                                       ),
                                                # if access type is free or paid show relevant button
                                                access_action_button(
                                                    info=info, page=page, navigate=navigate, media_view="document_view"),
                                                ft.IconButton(icon=ft.Icons.EDIT, icon_size=17, tooltip="edit", on_click=lambda e, i=info, content_type="DOCUMENT": handle_document_action(
                                                    e, "EDIT", i, page, navigate, content_type,)),  # opens page to edit content
                                            ]
                                        ),


                                        ft.Row(
                                            spacing=3,
                                            controls=[
                                                ft.Row(
                                                    spacing=4,
                                                    controls=[
                                                        ft.Icon(
                                                            ft.Icons.REMOVE_RED_EYE, size=16, ),
                                                        # number of viewers
                                                        ft.Text(
                                                            info.get("views_count", 0), size=12)
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-5,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.FAVORITE, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.RED,
                                                                      on_click=lambda e, i=info, content_type="DOCUMENT": handle_document_action(
                                                                          e, "FAVORITE", i, page, navigate, content_type, )  # call function that deals with like logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("likes_count", 0), size=12),
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-5,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.BLUE_600,
                                                                      on_click=lambda e, i=info, content_type="DOCUMENT": handle_document_action(
                                                                          e, "DOWNLOAD", i, page, navigate, content_type,)  # call function that deals with download logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("downloads_count", 0), size=12),
                                                    ]
                                                ),
                                            ]

                                        ),

                                    ]
                                )
                            ]
                        )
                    )
                )
            # end of for loop for documents

            # Row to hold the returned data
            my_podcast_list = ft.Row(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[]
            )
            # beginning of for loop for podcasts
            for info in podcasts:
                # check if document is free so that one has full accesss to free ones otherwise no access
                is_free = info.get("access_type") == "free"

                # inlude for subscription if person in subscribed table then allow access if not deny access

                # append the content in form of cards to the my_podcast_list
                my_podcast_list.controls.append(
                    ft.Container(
                        padding=24,
                        width=350,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=16,
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            color=ft.Colors.BLACK_12,
                            offset=ft.Offset(0, 4)
                        ),
                        content=ft.Row(
                            controls=[
                                ft.Image(
                                    src=info.get(
                                        "cover_url", f'https://picsum.photos/200/200?{info["id"]}'),  # image
                                    width=150,
                                    height=190,
                                    fit="contain",
                                    border_radius=ft.border_radius.all(10),
                                ),

                                ft.Column(
                                    expand=True,
                                    spacing=6,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(
                                                    info["title"],  # title
                                                    size=16,
                                                    expand=True,
                                                    weight=ft.FontWeight.BOLD,
                                                    max_lines=2,
                                                    overflow=ft.TextOverflow.ELLIPSIS
                                                ),
                                                ft.Row(spacing=-4,
                                                       controls=[
                                                           ft.IconButton(icon=ft.Icons.DELETE_FOREVER,
                                                                         icon_size=17,
                                                                         icon_color=ft.Colors.RED,
                                                                         tooltip="delete",
                                                                         on_click=lambda e, i=info, content_type="PODCAST": handle_document_action(e, "DELETE_POST", i, page, navigate, content_type,)),  # opens function that opens a dialogue to confirm post deleting
                                                       ]
                                                       ),
                                            ]
                                        ),

                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.PERSON_OUTLINE, size=16),
                                                ft.Text(
                                                    # authur
                                                    info.get(
                                                        "authur", "Unknown"),
                                                    size=12,
                                                    color=ft.Colors.BLUE_GREY_400
                                                ),
                                            ]
                                        ),

                                        ft.Text(
                                            # published date, call format_datetime() function to make date readable
                                            f'Published: {format_datetime(info.get("created_at", "N/A"))}',
                                            size=12,
                                            color=ft.Colors.BLUE_GREY_400
                                        ),

                                        ft.Text(
                                            # description if none show ....
                                            info.get("description", "..."),
                                            size=14,
                                            max_lines=3,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        ),

                                        ft.Row(
                                            spacing=3,
                                            controls=[
                                                ft.Row(spacing=-5,
                                                       controls=[
                                                           ft.IconButton(icon=ft.Icons.COMMENT_OUTLINED,
                                                                         tooltip="comments",
                                                                         on_click=lambda e, i=info, content_type="PODCAST": handle_document_action(e, "COMMENT", i, page, navigate, content_type,)),  # opens function that opens a dialogue
                                                           ft.Text(
                                                               info.get("comments_count", 0), size=12),
                                                       ]
                                                       ),
                                                # if access type is free or paid show relevant button
                                                access_action_button(
                                                    info=info, page=page, navigate=navigate, media_view="podcast_view"),
                                                ft.IconButton(icon=ft.Icons.EDIT, icon_size=17, tooltip="edit", on_click=lambda e, i=info, content_type="PODCAST": handle_document_action(
                                                    e, "EDIT", i, page, navigate, content_type,)),  # opens page to edit content
                                            ]
                                        ),


                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Row(
                                                    spacing=4,
                                                    controls=[
                                                        ft.Icon(
                                                            ft.Icons.REMOVE_RED_EYE, size=16, ),
                                                        # number of viewers
                                                        ft.Text(
                                                            info.get("views_count", 0), size=12)
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-4,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.FAVORITE, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.RED,
                                                                      on_click=lambda e, i=info, content_type="PODCAST": handle_document_action(
                                                                          e, "FAVORITE", i, page, navigate, content_type, )  # call function that deals with like logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("likes_count", 0), size=12),
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-4,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.BLUE_600,
                                                                      on_click=lambda e, i=info, content_type="PODCAST": handle_document_action(
                                                                          e, "DOWNLOAD", i, page, navigate, content_type,)  # call function that deals with download logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("downloads_count", 0), size=12),
                                                    ]
                                                ),
                                            ]
                                        ),

                                    ]
                                )
                            ]
                        )
                    )
                )
            # end of for loop for podcasts

            # list to hold the returned data
            my_video_list = ft.Row(
                spacing=16,
                scroll=ft.ScrollMode.AUTO,
                controls=[]
            )
            # beginning of for loop for videos
            for info in videos:
                # check if document is free so that one has full accesss to free ones otherwise no access
                is_free = info.get("access_type") == "free"

                # inlude for subscription if person in subscribed table then allow access if not deny access

                # append the content in form of cards to the my_video_list
                my_video_list.controls.append(
                    ft.Container(
                        padding=24,
                        width=350,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=16,
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            color=ft.Colors.BLACK_12,
                            offset=ft.Offset(0, 4)
                        ),
                        content=ft.Row(
                            controls=[
                                ft.Image(
                                    src=info.get(
                                        "cover_url", f'https://picsum.photos/200/200?{info["id"]}'),  # image
                                    width=150,
                                    height=190,
                                    fit="contain",
                                    border_radius=ft.border_radius.all(10),
                                ),

                                ft.Column(
                                    expand=True,
                                    spacing=6,
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Text(
                                                    info["title"],  # title
                                                    size=16,
                                                    expand=True,
                                                    weight=ft.FontWeight.BOLD,
                                                    max_lines=2,
                                                    overflow=ft.TextOverflow.ELLIPSIS
                                                ),
                                                ft.Row(spacing=-4,
                                                       controls=[
                                                           ft.IconButton(icon=ft.Icons.DELETE_FOREVER,
                                                                         icon_size=17,
                                                                         icon_color=ft.Colors.RED,
                                                                         tooltip="delete",
                                                                         on_click=lambda e, i=info, content_type="VIDEO": handle_document_action(e, "DELETE_POST", i, page, navigate, content_type,)),  # opens function that opens a dialogue to confirm post deleting
                                                       ]
                                                       ),
                                            ]
                                        ),

                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.PERSON_OUTLINE, size=16),
                                                ft.Text(
                                                    # authur
                                                    info.get(
                                                        "authur", "Unknown"),
                                                    size=12,
                                                    color=ft.Colors.BLUE_GREY_400
                                                ),
                                            ]
                                        ),

                                        ft.Text(
                                            # published date, call format_datetime() function to make date readable
                                            f'Published: {format_datetime(info.get("created_at", "N/A"))}',
                                            size=12,
                                            color=ft.Colors.BLUE_GREY_400
                                        ),

                                        ft.Text(
                                            # description if none show ....
                                            info.get("description", "..."),
                                            size=14,
                                            max_lines=3,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        ),

                                        ft.Row(
                                            spacing=3,
                                            controls=[
                                                ft.Row(spacing=-5,
                                                       controls=[
                                                           ft.IconButton(icon=ft.Icons.COMMENT_OUTLINED,
                                                                         tooltip="comments",
                                                                         on_click=lambda e, i=info, content_type="VIDEO": handle_document_action(e, "COMMENT", i, page, navigate, content_type,)),  # opens function that opens a dialogue
                                                           ft.Text(
                                                               info.get("comments_count", 0), size=12),
                                                       ]
                                                       ),
                                                # if access type is free or paid show relevant button
                                                access_action_button(
                                                    info=info, page=page, navigate=navigate, media_view="video_view"),
                                                ft.IconButton(icon=ft.Icons.EDIT, icon_size=17, tooltip="edit", on_click=lambda e, i=info, content_type="VIDEO": handle_document_action(
                                                    e, "EDIT", i, page, navigate, content_type,)),  # opens page to edit content
                                            ]
                                        ),


                                        ft.Row(
                                            spacing=4,
                                            controls=[
                                                ft.Row(
                                                    spacing=4,
                                                    controls=[
                                                        ft.Icon(
                                                            ft.Icons.REMOVE_RED_EYE, size=16, ),
                                                        # number of viewers
                                                        ft.Text(
                                                            info.get("views_count", 0), size=12)
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-4,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.FAVORITE, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.RED,
                                                                      on_click=lambda e, i=info, content_type="VIDEO": handle_document_action(
                                                                          e, "FAVORITE", i, page, navigate, content_type, )  # call function that deals with like logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("likes_count", 0), size=12),
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-4,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.BLUE_600,
                                                                      on_click=lambda e, i=info, content_type="VIDEO": handle_document_action(
                                                                          e, "DOWNLOAD", i, page, navigate, content_type,)  # call function that deals with download logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("downloads_count", 0), size=12),
                                                    ]
                                                ),
                                            ]
                                        ),

                                    ]
                                )
                            ]
                        )
                    )
                )
            # end of for loop for videos

            message = ft.Text("", visible=False)  # flashed messages variable

            details = ft.Container(
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[

                        # container simple nav bar
                        ft.Column(
                            expand=True,
                            controls=[
                                ft.Container(
                                    content=ft.Row(
                                        expand=True,
                                        controls=[
                                            ft.TextButton("Setings", icon=ft.Icons.SETTINGS, icon_color=ft.Colors.BLUE_GREY_900, on_click=lambda e: page.run_task(
                                                navigate, "/settings"), expand=True),
                                            ft.TextButton("Wallet", icon=ft.Icons.WALLET, icon_color=ft.Colors.AMBER_900, on_click=lambda e: page.run_task(
                                                navigate, "/wallet"), expand=True),
                                            # call logout function.. it clears client storage and takes to login page
                                            ft.TextButton(
                                                "logut", icon=ft.Icons.LOGOUT_OUTLINED, icon_color=ft.Colors.LIGHT_BLUE_900, on_click=log_out, expand=True)
                                        ]
                                    )
                                ),
                            ]
                        ),

                        message,  # flashed message are called here

                        # container for documents
                        ft.Container(
                            expand=True,
                            border_radius=ft.BorderRadius.all(20),
                            padding=10,
                            content=ft.Column(
                                scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                                controls=[
                                    # container simple nav bar with button to upload a new document
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Text("My Documents", size=24,
                                                        weight=ft.FontWeight.W_600),

                                            ]
                                        )
                                    ),
                                    my_document_list  # 👈 call ListView directly here
                                ]
                            )
                        ),


                        # container for podcasts
                        ft.Container(
                            expand=True,
                            border_radius=ft.BorderRadius.all(20),
                            padding=10,
                            content=ft.Column(
                                scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                                controls=[
                                    # container simple nav bar with button to upload a new document
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Text("My Podcasts", size=24,
                                                        weight=ft.FontWeight.W_600),

                                            ]
                                        )
                                    ),
                                    my_podcast_list  # 👈 call ListView directly here
                                ]
                            )
                        ),

                        # container for videos
                        ft.Container(
                            expand=True,
                            border_radius=ft.BorderRadius.all(20),
                            padding=10,
                            content=ft.Column(
                                scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                                controls=[
                                    # container simple nav bar with button to upload a new document
                                    ft.Container(
                                        content=ft.Row(
                                            controls=[
                                                ft.Text("My Videos", size=24,
                                                        weight=ft.FontWeight.W_600),

                                            ]
                                        )
                                    ),
                                    my_video_list  # 👈 call ListView directly here
                                ]
                            )
                        ),

                    ]
                )
            )

            return ft.View(
                route="/account",
                controls=[
                    top_bar(page, navigate),
                    details,
                    bottom_bar(page, navigate, active="account")
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
                route="/account",
                controls=[
                    top_bar(page, navigate),
                    details,
                    bottom_bar(page, navigate, active="account")
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
                route="/account",
                controls=[
                    top_bar(page, navigate),
                    details,
                    bottom_bar(page, navigate, active="account")
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
            route="/account",
            controls=[
                top_bar(page, navigate),
                details,
                bottom_bar(page, navigate, active="account")
            ]
        )
