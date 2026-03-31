import flet as ft
from router import build_view

async def main(page: ft.Page):
    
    async def navigate(route: str):
        await page.push_route(route)

    async def route_change(e):
        page.views.clear()
        view = await build_view(page, navigate)
        if view:
            page.views.append(view)
        page.update()

    def view_pop(view):
        page.views.pop()
        page.run_task(navigate, page.views[-1].route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    await page.push_route("/home")

ft.run(main)
