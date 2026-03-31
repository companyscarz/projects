import flet as ft
import requests
from datetime import datetime
from components.nav_bar import bottom_bar, top_bar


async def podcasts(page, navigate):

    # get the token from client storage and pass them as headers
    client_token = await page.shared_preferences.get("digital_read_user_token")
    content_type = "PODCAST"

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

        # make request to backend to get comments of this specific podcast
        res = requests.get(
            f"http://127.0.0.1:8080/get_comments/{content_type}/{content_id}",
            headers={
                "token": client_token
            }
        )
        response = res.json()  # Convert JSON to Python dict
        podcast_comments = response.get(
            "get_comments", [])  # get podcasts data

        # if response is 200, everything is ok.. continue
        if res.status_code == 200:
            for comments in podcast_comments:
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

    def access_action_button(info, page, navigate):
        # if access_type for the podcast is free then access button is changed and color to show that is free to continue to read,
        # when clicked go to the podcast_view page passing media id there
        if info["access_type"] == "free" or subscribed:
            return ft.Button(
                "LISTEN",
                expand=True,
                align=ft.Alignment.CENTER,
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN_600,
                tooltip="Open podcast",
                on_click=lambda e: page.run_task(
                    # route_name,podcast(content)_id, user_id, username,
                    navigate, f"/podcast_view/{info['id']}/{user['id']}/{user['username']}"
                )
            )
        else:
            # if paid content change icons respectively
            # in future check if user_id is in subsribtion table then allow access if not there deny
            return ft.ElevatedButton(
                "Subscribe",
                scale=0.75,
                bgcolor=ft.Colors.AMBER_600,
                color=ft.Colors.BLACK,
                icon=ft.Icons.LOCK_OUTLINE,
                on_click=lambda e: page.run_task(navigate, "/wallet"),
            )


# _________________________--------------------logic for sction buttons-------------------------_________________________________


    def handle_podcast_action(e, action, info, page, navigate):
        # when comment section is clicked then open a dialogue box having comments on the content and a field box allowing one who subscribed to comment
        if action == "COMMENT":
            open_comments_dialog(page, user_id=str(
                user["id"]), username=user["username"], content_id=info["id"])
            # page.run_task(navigate, f"/podcast/{info['id']}/comments")
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
                        "content_type": content_type,
                        "content_id": f"{info['id']}",
                        "user_id": f"{info['id']}"
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

                elif response.status_code == 402:
                    message.color = ft.Colors.BLUE_600
                    message.value = "Unfavorited podcast"

                elif response.status_code == 500:
                    message.color = ft.Colors.RED_600
                    message.value = "Internal server error"

            except Exception as e:
                pass
            # adds a row to likes table in database, then gets them to get the number
            # if user already liked podcast then delete the row of id matching content, and user id matching
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
                    message.value = f"Podcast Downloaded"

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

    # get data from the backend and post it on the page
    try:
        # get token from client storage and pass them as headers
        res = requests.get(
            f"http://127.0.0.1:8080/get_content/{content_type}",
            headers={
                "token": client_token
            }
        )

        if res.status_code == 200:
            response = res.json()  # Convert JSON to Python dict

            podcasts = response.get("podcasts", [])  # get podcasts data
            user = response.get("user_details", [])  # get user details
            # check is user is subscribed or not
            subscribed = response.get("subscribed")
            subscribed = subscribed

            # list to hold the returned data
            data_list = ft.ListView(
                expand=True,
                spacing=16,
                padding=16,
                auto_scroll=False,
                clip_behavior=ft.ClipBehavior.HARD_EDGE
            )
            # loop through the returned data and show it inform of cards in the data_lst variable
            for info in podcasts:
                # check if podcast is free so that one has full accesss to free ones otherwise no access
                is_free = info.get("access_type") == "free"

                # inlude for subscription if person in subscribed table then allow access if not deny access

                # append the content in form of cards to the data_list
                data_list.controls.append(
                    ft.Container(
                        padding=24,
                        bgcolor=ft.Colors.WHITE,
                        border_radius=16,
                        shadow=ft.BoxShadow(
                            blur_radius=15,
                            color=ft.Colors.BLACK_12,
                            offset=ft.Offset(0, 4)
                        ),
                        alignment=ft.Alignment.CENTER,
                        content=ft.Row(
                            controls=[
                                ft.Column(
                                    expand=True,
                                    spacing=1,
                                    controls=[
                                        ft.Text(
                                            info["title"],  # title
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                            max_lines=2,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        ),

                                        ft.Row(
                                            controls=[
                                                ft.Icon(
                                                    ft.Icons.PERSON_OUTLINE, size=16),
                                                ft.Text(
                                                    # author
                                                    info.get(
                                                        "authur", "Unknown"),
                                                    size=12,
                                                    color=ft.Colors.BLUE_GREY_400
                                                ),
                                                ft.Divider(),
                                                ft.Text(
                                                    # published date, call format_datetime() function to make date readable
                                                    f'_: {format_datetime(info.get("created_at", "N/A"))}',
                                                    size=12,
                                                    color=ft.Colors.BLUE_GREY_400
                                                ),
                                            ]
                                        ),

                                        ft.Image(
                                            src=info.get(
                                                "cover_url", f'https://picsum.photos/200/200?{info["id"]}'),  # image
                                            width=150,
                                            height=190,
                                            fit="contain",
                                            align=ft.Alignment.CENTER,
                                            border_radius=ft.border_radius.all(
                                                10),
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
                                                        like_icon := ft.IconButton(icon=ft.Icons.FAVORITE, icon_size=16,
                                                                                   # DISABLED IF NOT SUBSCRIBED
                                                                                   icon_color=ft.Colors.RED if (
                                                                                       is_free or subscribed) else ft.Colors.GREY_600,
                                                                                   disabled=(
                                                                                       not is_free or not subscribed),
                                                                                   on_click=lambda e, i=info: handle_podcast_action(
                                                                                       e, "FAVORITE", i, page, navigate)  # call function that deals with like logic
                                                                                   ),
                                                        likes_count := ft.Text(
                                                            info.get("likes_count", 0), size=12),
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-5,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.DOWNLOAD, icon_size=16,
                                                                      # DISABLED IF NOT SUBSCRIBED
                                                                      icon_color=ft.Colors.BLUE_600 if (
                                                                          is_free or subscribed) else ft.Colors.GREY_600,
                                                                      disabled=(
                                                                          not is_free or not subscribed),
                                                                      on_click=lambda e, i=info: handle_podcast_action(
                                                                          e, "DOWNLOAD", i, page, navigate)  # call function that deals with download logic
                                                                      ),
                                                        ft.Text(
                                                            info.get("downloads_count", 0), size=12),
                                                    ]
                                                ),
                                                ft.Row(
                                                    spacing=-5,
                                                    controls=[
                                                        ft.IconButton(icon=ft.Icons.COMMENT_OUTLINED,
                                                                      tooltip="comments",
                                                                      on_click=lambda e, i=info: handle_podcast_action(e, "COMMENT", i, page, navigate)),  # opens function that opens a dialogue
                                                        comments_count := ft.Text(
                                                            info.get("comments_count", 0), size=12),
                                                    ]
                                                )
                                            ]
                                        ),
                                        ft.Row(
                                            spacing=3,
                                            controls=[
                                                # if access type is free or paid show relevant button
                                                access_action_button(
                                                    info, page, navigate),
                                            ]
                                        ),
                                    ]
                                )
                            ]
                        )
                    )
                )

            message = ft.Text("", visible=False)  # flashed messages variable

            # where all the controls(widgets) are brought together then returned for viewing
            details = ft.Container(
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=10,
                content=ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[
                        # container simple nav bar with button to upload a new podcast
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.FloatingActionButton(icon=ft.Icons.ADD_CIRCLE_OUTLINED, on_click=lambda e: page.run_task(
                                        navigate, "/upload_podcast"), ),
                                    message,  # flashed message are called here
                                ]
                            )
                        ),
                        data_list  # 👈 call ListView directly here
                    ]
                )
            )
            return ft.View(
                route="/podcasts",
                controls=[
                    top_bar(page, navigate,),
                    details,
                    bottom_bar(page, navigate, active="podcasts"),
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
                        # container for podcasts
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
                route="/podcasts",
                controls=[
                    top_bar(page, navigate,),
                    details,
                    bottom_bar(page, navigate, active="podcasts"),
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
                        # container for podcasts
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
                route="/podcasts",
                controls=[
                    top_bar(page, navigate,),
                    details,
                    bottom_bar(page, navigate, active="podcasts"),
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
                    # container for podcasts
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
            route="/podcasts",  # route for podcasts
            controls=[
                top_bar(page, navigate,),  # topbar for digital_read
                details,  # content about digital read podcasts
                # bottom nav bar
                bottom_bar(page, navigate, active="podcasts"),
            ]
        )
