import flet as ft
import flet_audio as fta


def podcast_player(page: ft.Page,
                   audio_url="https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                   cover_url="https://picsum.photos/300/300",
                   title="Sample Podcast Episode",
                   author="John Doe"):

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # ----------- State -----------
    duration_ms = 0
    position_ms = 0
    is_playing = False

    # ----------- Helpers -----------
    def format_time(ms):
        seconds = int(ms / 1000)
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    # ----------- UI Elements -----------
    progress_text = ft.Text("00:00")
    duration_text = ft.Text("00:00")

    async def seek_audio(e):
        if duration_ms > 0:
            seek_position = (progress_bar.value / 100) * duration_ms
            await audio.seek(ft.Duration(milliseconds=int(seek_position)))

    progress_bar = ft.Slider(
        min=0,
        max=100,
        value=0,
        expand=True,
        on_change_end=seek_audio,
    )

    play_button = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW,
        icon_size=50,
    )

    # ----------- Audio Handlers -----------

    async def play_pause(e):
        nonlocal is_playing

        if is_playing:
            await audio.pause()
            play_button.icon = ft.Icons.PLAY_ARROW
            is_playing = False
        else:
            await audio.play()  # play first time
            play_button.icon = ft.Icons.PAUSE
            is_playing = True

        page.update()

    async def on_position_change(e):
        nonlocal position_ms
        position_ms = e.position.in_milliseconds()

        if duration_ms > 0:
            progress_bar.value = (position_ms / duration_ms) * 100
            progress_text.value = format_time(position_ms)
            page.update()

    async def on_duration_change(e):
        nonlocal duration_ms
        duration_ms = e.duration.in_milliseconds()
        duration_text.value = format_time(duration_ms)
        page.update()

    # Attach handler to play button
    play_button.on_click = play_pause

    # ----------- Audio Object -----------
    audio = fta.Audio(
        src=audio_url,
        autoplay=False,
        volume=1,
        release_mode=fta.ReleaseMode.STOP,
        on_position_change=on_position_change,
        on_duration_change=on_duration_change,
    )

    # ----------- Layout -----------

    return ft.Container(
        width=350,
        padding=25,
        border_radius=25,
        bgcolor=ft.Colors.GREY_200,
        content=ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
            controls=[
                # Cover
                ft.Container(
                    width=250,
                    height=250,
                    border_radius=25,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=cover_url,
                    ),
                ),

                # Title
                ft.Text(title, size=22, weight=ft.FontWeight.BOLD),

                # Author
                ft.Text(author, size=14, color=ft.Colors.GREY_600),

                # Time row
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[progress_text, duration_text],
                ),

                progress_bar,

                # Controls
                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=40,
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.REPLAY_10,
                            icon_size=30,
                            on_click=lambda e: audio.seek(
                                ft.Duration(milliseconds=max(
                                    0, position_ms - 10000))
                            ),
                        ),
                        play_button,
                        ft.IconButton(
                            icon=ft.Icons.FORWARD_10,
                            icon_size=30,
                            on_click=lambda e: audio.seek(
                                ft.Duration(
                                    milliseconds=position_ms + 10000)
                            ),
                        ),
                    ],
                ),
            ],
        ),
    )
