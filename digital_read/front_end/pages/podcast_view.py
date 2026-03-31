import flet as ft
import flet_audio as fta
import requests
from datetime import datetime
from components.nav_bar import top_bar, bottom_bar
# from components.players import podcast_player

# pass the page, navigate podcast(content)_id, user_id, username,


async def podcast_view(page, navigate, content_id, user_id, username):

    # align text in center
    # page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # sample data
    audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"
    cover_url = "https://picsum.photos/300/300"
    title = "Sample Podcast Episode"
    author = "John Doe"

    # get token and describe the content type
    client_token = await page.shared_preferences.get("digital_read_user_token")
    content_type = "PODCAST"

    # ================= STATE =================
    duration_ms = 0
    position_ms = 0
    is_playing = False

    # ================= TIME FORMAT =================

    def format_time(ms):
        seconds = int(ms / 1000)
        return f"{seconds // 60:02}:{seconds % 60:02}"

    # ================= AUDIO EVENTS =================
    def get_ms(value):
        # If already int → return it
        if isinstance(value, int):
            return value

        # If Duration object with property
        if hasattr(value, "in_milliseconds"):
            ms = value.in_milliseconds
            return ms() if callable(ms) else ms

        return 0

    def on_duration_change(e):
        nonlocal duration_ms
        duration_ms = get_ms(e.duration)
        # call the event action when duration change is == to 15%
        # content has been viewed

        progress.max = max(duration_ms, 1)
        total_time.value = format_time(duration_ms)

        page.update()

    def on_position_change(e):
        nonlocal position_ms

        position_ms = get_ms(e.position)

        # Clamp position so it never exceeds duration
        if duration_ms > 0:
            position_ms = min(position_ms, duration_ms)

        progress.value = position_ms
        current_time.value = format_time(position_ms)

        # If audio finished, reset play button
        if duration_ms > 0 and position_ms >= duration_ms:
            play_button.icon = ft.Icons.PLAY_ARROW

        page.update()

    # ================= CONTROLS =================

    async def toggle_play(e):
        nonlocal is_playing
        if is_playing:
            await audio.pause()
            play_button.icon = ft.Icons.PLAY_ARROW
            is_playing = False
        else:
            await audio.resume()
            play_button.icon = ft.Icons.PAUSE
            is_playing = True
        page.update()

    async def forward_2s(e):
        new_pos = min(duration_ms, position_ms + 2000)
        await audio.seek(ft.Duration(milliseconds=new_pos))

    async def backward_2s(e):
        new_pos = max(0, position_ms - 2000)
        await audio.seek(ft.Duration(milliseconds=new_pos))

    async def slider_seek(e):
        await audio.seek(ft.Duration(milliseconds=int(e.control.value)))

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

        # make request to backend to get comments of this specific video
        res = requests.get(
            f"http://127.0.0.1:8080/get_comments/{content_type}/{content_id}",
            headers={
                "token": client_token
            }
        )
        response = res.json()  # Convert JSON to Python dict
        podcast_comments = response.get("get_comments", [])  # get videos data
        print(podcast_comments)

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

    # _________________________--------------------logic for sction buttons-------------------------_________________________________
    def handle_video_action(e, action, page, navigate):
        # when comment section is clicked then open a dialogue box having comments on the content and a field box allowing one who subscribed to comment
        if action == "COMMENT":
            open_comments_dialog(page, user_id=user_id,
                                 username=username, content_id=content_id)
            # page.run_task(navigate, f"/podcast/{content_id}/comments")
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
                        "content_id": content_id,
                        "user_id": user_id
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

    # ------------------ STOP AUDIO ON PAGE LEAVE ------------------

    def cleanup_audio(e):
        if hasattr(page, "services") and audio in page.services:
            audio.stop()  # stop playback
            page.services.remove(audio)
        print("Audio stopped because page changed or closed")

    try:
        res = requests.get(
            f"http://127.0.0.1:8080/one_content/{content_id}/{content_type}",
            headers={"token": client_token}
        )

        if res.status_code == 200:

            response = res.json()  # Convert JSON to Python dict
            podcast_info = response.get(
                "podcasts", [])  # get documents data

            message = ft.Text("", visible=False)  # flashed messages variable

            # ================= AUDIO =================
            audio = fta.Audio(
                src=audio_url,
                autoplay=False,
                release_mode=fta.ReleaseMode.STOP,
                on_loaded=lambda _: print("Loaded"),
            )

            audio.on_duration_change = on_duration_change
            audio.on_position_change = on_position_change

            # close the audio immediately the page changes

    # ------------------ STOP AUDIO ON PAGE LEAVE ------------------
            def cleanup_audio(e):
                if hasattr(page, "services") and audio in page.services:
                    audio.stop()  # stop playback
                    page.services.remove(audio)
                print("Audio stopped because page changed or closed")
            page.on_dispose = cleanup_audio

            # ================= UI =================

            play_button = ft.IconButton(
                icon=ft.Icons.PLAY_ARROW,
                icon_size=40,
                on_click=toggle_play,
            )

            progress = ft.Slider(
                min=0,
                max=1,
                value=0,
                on_change=slider_seek,  # responds while sliding
                active_color="#6366f1",
            )

            current_time = ft.Text("00:00")
            total_time = ft.Text("00:00")

            details = ft.Container(
                expand=True,
                border_radius=ft.BorderRadius.all(20),
                padding=20,
                content=ft.Column(
                    scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
                    controls=[
                        # container for videos should contain the podcast and a button that when clicked shows the reaction options
                        ft.Container(
                            padding=25,
                            border_radius=20,
                            content=ft.Column(
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    cover := ft.Container(
                                        width=250,
                                        height=250,
                                        border_radius=20,
                                        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                        content=ft.Image(
                                            src=cover_url,
                                            fit=ft.BoxFit.COVER,
                                        ),
                                        bgcolor=ft.Colors.BLACK
                                    ),

                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                        controls=[current_time, total_time],
                                    ),

                                    progress,

                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=20,
                                        controls=[
                                            ft.IconButton(
                                                icon=ft.Icons.REPLAY_10,
                                                on_click=backward_2s,
                                            ),
                                            play_button,
                                            ft.IconButton(
                                                icon=ft.Icons.FORWARD_10,
                                                on_click=forward_2s,
                                            ),
                                        ],
                                    ),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                                        controls=[
                                            like_icon := ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.IconButton(
                                                        icon=ft.Icons.FAVORITE_BORDER,
                                                        icon_color=ft.Colors.RED,
                                                        on_click=lambda e: handle_video_action(
                                                            e, "FAVORITE", page, navigate),
                                                    ),
                                                    likes_count := ft.Text(
                                                        podcast_info.get("likes_count", 0), size=12)
                                                ]
                                            ),
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.IconButton(
                                                        icon=ft.Icons.COMMENT_OUTLINED,
                                                        on_click=lambda e: handle_video_action(
                                                            e, "COMMENT", page, navigate),
                                                    ),
                                                    comments_count := ft.Text(
                                                        podcast_info.get("comments_count", 0), size=12)
                                                ]
                                            ),
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.REMOVE_RED_EYE,
                                                        size=18,
                                                        color=ft.Colors.BLUE_GREY_600
                                                    ),
                                                    ft.Text(
                                                        podcast_info.get("views_count", 0), size=12)
                                                ]
                                            ),
                                            ft.Column(
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.DOWNLOAD,
                                                        size=18,
                                                        color=ft.Colors.BLUE_600
                                                    ),
                                                    ft.Text(
                                                        podcast_info.get("downloads_count", 0), size=12)
                                                ]
                                            ),
                                        ],
                                    ),
                                    message,
                                ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route=f"/podcast_view/{content_id}",
                controls=[
                    top_bar(page, navigate,),
                    details,
                    bottom_bar(page, navigate, active="podcasts"),
                ],
            )

        elif res.status_code == 401:
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
                                ft.Text(f"Error!", size=22,
                                        weight=ft.FontWeight.BOLD,),
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route=f"/podcast_view/{content_id}",
                controls=[
                    top_bar(page, navigate,),  # topbar for digital_read
                    details,
                    # bottom nav bar
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
                                ft.Text(f"Unkown Error!", size=22,
                                        weight=ft.FontWeight.BOLD,),
                            ]),
                        ),
                    ]
                )
            )

            return ft.View(
                route=f"/podcast_view/{content_id}",
                controls=[
                    top_bar(page, navigate,),  # topbar for digital_read
                    details,
                    # bottom nav bar
                    bottom_bar(page, navigate, active="podcasts"),
                ]
            )

    except RuntimeError:
        print("runtime error")
        pass
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
            route=f"/podcast_view/{content_id}",
            controls=[
                top_bar(page, navigate,),  # topbar for digital_read
                # bottom nav bar
                bottom_bar(page, navigate, active="podcasts"),
            ]
        )
