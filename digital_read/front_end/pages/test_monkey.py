import flet as ft
from flet_webview import WebView


def main(page: ft.Page):

    pdf_url = "https://pandas.pydata.org/pandas-docs/version/1.4.4/pandas.pdf"
    viewer_url = f"https://docs.google.com/gview?embedded=true&url={pdf_url}"

    page.add(
        WebView(url=viewer_url),
    )


ft.run(main)
