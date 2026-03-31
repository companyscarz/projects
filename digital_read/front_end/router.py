import inspect

from pages.login import login_view
from pages.signup import signup_view
from pages.home import home_view
from pages.account import account
from pages.documents import documents
from pages.podcasts import podcasts
from pages.videos import videos
from pages.settings import settings
from pages.upload_document import upload_document
from pages.upload_podcast import upload_podcast
from pages.upload_video import upload_video
from pages.document_view import document_view
from pages.podcast_view import podcast_view
from pages.video_view import video_view
from pages.wallet import my_wallet
from pages.edit_content import edit_content


async def build_view(page, navigate):

    # 🔹 HANDLE DYNAMIC DOCUMENT ROUTE FIRST
    if page.route.startswith("/document_view/"):
        document_id = page.route.split("/")[-3]
        user_id = page.route.split("/")[-2]
        username = page.route.split("/")[-1]
        return await document_view(page, navigate, document_id, user_id, username)
    elif page.route.startswith("/podcast_view/"):
        podcast_id = page.route.split("/")[-3]
        user_id = page.route.split("/")[-2]
        username = page.route.split("/")[-1]
        return await podcast_view(page, navigate, podcast_id, user_id, username)
    elif page.route.startswith("/video_view/"):
        video_id = page.route.split("/")[-3]
        user_id = page.route.split("/")[-2]
        username = page.route.split("/")[-1]
        return await video_view(page, navigate, video_id, user_id, username)
    elif page.route.startswith("/edit_content/"):
        content_id = page.route.split("/")[-8]
        title = page.route.split("/")[-7]
        theme = page.route.split("/")[-6]
        level = page.route.split("/")[-5]
        description = page.route.split("/")[-4]
        access_type = page.route.split("/")[-3]
        cover_path = page.route.split("/")[-2]
        content_type = page.route.split("/")[-1]
        return await edit_content(page, navigate, content_id, title, theme, level, description, access_type, cover_path, content_type)

    routes = {
        "/login": login_view,
        "/signup": signup_view,
        "/home": home_view,
        "/account": account,
        "/documents": documents,
        "/podcasts": podcasts,
        "/videos": videos,
        "/settings": settings,
        "/upload_document": upload_document,
        "/upload_podcast": upload_podcast,
        "/upload_video": upload_video,
        "/document_view": document_view,
        "/podcast_view": podcast_view,
        "/video_view": video_view,
        "/wallet": my_wallet,
        "/edit_content": edit_content
    }

    view_builder = routes.get(page.route)
    if not view_builder:
        return None

    # 🔒 SAFE handling of sync vs async views
    if inspect.iscoroutinefunction(view_builder):
        return await view_builder(page, navigate)
    else:
        return view_builder(page, navigate)
