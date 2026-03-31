import flet as ft
import requests
import time
import asyncio


def open_payment_sheet(page, navigate, subscription_plan, amount, action):

    def close_sheet(e):
        e.control.page.pop_dialog()
        return

    def withdraw(e):
        alert_message.visible = True
        alert_message.color = ft.Colors.GREEN_600
        alert_message.value = f"Still in Construction"

    # retreies upto 3 minutes to check the status of the payment every 5 seconds, if successful return success message and navigate to account page, if failed return failed message, if timeout return timeout message
    async def poll_payment_status(tx_ref):
        max_attempts = 36  # 3 minutes
        attempts = 0

        while attempts < max_attempts:
            try:
                status_response = await asyncio.to_thread(
                    requests.get,
                    f"http://127.0.0.1:8080/payment-status/{tx_ref}"
                )

                if status_response.status_code == 200:
                    data = status_response.json()
                    status = data.get("status")

                    if status == "successful":
                        alert_message.visible = True
                        alert_message.color = ft.Colors.GREEN_600
                        alert_message.value = "Payment successful!"
                        page.update()
                        await asyncio.sleep(2)
                        page.run_task(navigate, "/account")
                        return

                    elif status == "failed":
                        alert_message.visible = True
                        alert_message.color = ft.Colors.RED_600
                        alert_message.value = "Payment failed."
                        telephone_number.value = ""
                        page.update()
                        return

                alert_message.visible = True
                alert_message.color = ft.Colors.RED_600
                alert_message.value = "Reconnecting..."
                await asyncio.sleep(5)
                attempts += 1

            except Exception:
                alert_message.visible = True
                alert_message.color = ft.Colors.RED_600
                alert_message.value = "Connection error while checking status."
                page.update()
                return

        alert_message.visible = True
        alert_message.color = ft.Colors.ORANGE_600
        alert_message.value = "Payment timeout. Please try again."
        page.update()

    async def subscribe(e):

        # get the token from client storage and pass them as headers
        client_token = await page.shared_preferences.get("digital_read_user_token")

        try:
            response = requests.post(
                "http://127.0.0.1:8080/subscribe",
                json={
                    "client_token": client_token,
                    "subscription_plan": subscription_plan,
                    "amount": amount,
                    "phone_number": telephone_number.value,
                    "payment_method": payment_systems.value
                }
            )

            if response.status_code == 200:

                data = response.json()
                tx_ref = data.get("tx_ref")

                alert_message.visible = True
                alert_message.color = ft.Colors.GREEN_600
                alert_message.value = "Payment initiated. Complete on your phone."
                page.update()
                # Start polling
                page.run_task(poll_payment_status, tx_ref)
                return

            elif response.status_code == 400:
                alert_message.visible = True
                alert_message.color = ft.Colors.RED_600
                alert_message.value = "Some content is missing"
                return

            elif response.status_code == 401 or not client_token:
                alert_message.visible = True
                alert_message.color = ft.Colors.RED_600
                alert_message.value = "Invalid email or password."
                page.run_task(navigate, "/login")
                return

            elif response.status_code == 402:
                alert_message.visible = True
                alert_message.color = ft.Colors.BLUE_600
                alert_message.value = "Already on a subscription plan."
                return

            else:
                alert_message.visible = True
                alert_message.color = ft.Colors.RED_600
                alert_message.value = "Unkown Error!."
                return

        except Exception as e:
            alert_message.visible = True
            alert_message.color = ft.Colors.RED_600
            alert_message.value = "Connection error."
            return

    def build_payment_fields(method):
        if method == "MOBILE MONEY":
            title.value = "Enter your mobile money phone number"
            payment_systems.visible = False
            telephone_number.visible = True
            telephone_number.label = "Your mobile money"
            alert_message.visible = False
            back_btn.visible = True
            MOBILEMONEY_payment.visible = True

        elif method == "MPESA":
            title.value = "Enter your MPESA phone number"
            payment_systems.visible = False
            telephone_number.visible = True
            telephone_number.label = "Your MPESA number"
            alert_message.visible = False
            back_btn.visible = True
            MPESA_payment.visible = True

        elif method == "CARD":
            title.value = "Enter your CARD details."
            payment_systems.visible = False
            card_number.visible = True
            expiry_date.visible = True
            CVV_password.visible = True
            alert_message.visible = False
            back_btn.visible = True
            CARD_payment.visible = True

    def go_back(e):
        title.value = "Choose another payment system."
        payment_systems.visible = True
        telephone_number.visible = False
        telephone_number.value = ""
        card_number.visible = False
        card_number.value = ""
        expiry_date.visible = False
        expiry_date.value = ""
        CVV_password.visible = False
        CVV_password.value = ""
        MOBILEMONEY_payment.visible = False
        MPESA_payment.visible = False
        CARD_payment.visible = False
        back_btn.visible = False

    # controls arrangement
    cancel = ft.TextButton("Cancel", icon_color=ft.Colors.GREY_900,
                           icon=ft.Icons.CANCEL, on_click=close_sheet)
    title = ft.Text("Choose your payment system",
                    weight=ft.FontWeight.W_600, size=15)
    payment_systems = ft.Dropdown(
        width=200,
        value="Choose",
        on_select=lambda e: build_payment_fields(method=payment_systems.value),
        options=[
            ft.dropdown.Option("Choose"),
            ft.dropdown.Option("MOBILE MONEY"),
            ft.dropdown.Option("MPESA"),
            ft.dropdown.Option("CARD"),
        ],
    )
    telephone_number = ft.TextField(label="Number", width=250,
                                    autofocus=True, keyboard_type=ft.KeyboardType.PHONE, visible=False)
    card_number = ft.TextField(
        label="Card Number", width=250, visible=False, autofocus=True,)
    expiry_date = ft.TextField(label="Expiry Date", width=120, visible=False)
    CVV_password = ft.TextField(
        label="CVV", password=True, width=120, visible=False)
    alert_message = ft.Text("", visible=False)
    # proceed = ft.Button("Proceed", bgcolor=ft.Colors.BLUE_600, color=ft.Colors.WHITE,
    #                   on_click=lambda e: build_payment_fields(method=payment_systems.value), visible=True)

    MOBILEMONEY_payment = ft.Button("MOBILE MONEY", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE, on_click=(
        subscribe if action == "SUBSCRIBE" else withdraw), visible=False)
    MPESA_payment = ft.Button("MPESA Pay", bgcolor=ft.Colors.GREEN_600, color=ft.Colors.WHITE, on_click=(
        subscribe if action == "SUBSCRIBE" else withdraw), visible=False)
    CARD_payment = ft.Button("Card Pay", bgcolor=ft.Colors.BLACK, color=ft.Colors.WHITE, on_click=(
        subscribe if action == "SUBSCRIBE" else withdraw), visible=False)

    back_btn = ft.Button("Back", bgcolor=ft.Colors.BLUE_GREY_900,
                         color=ft.Colors.WHITE, on_click=go_back, visible=False)

    details = ft.Column(
        scroll=ft.ScrollMode.ALWAYS,  # enable scrolling
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=300,
        controls=[
            ft.Row(alignment=ft.MainAxisAlignment.END, controls=[cancel,]),
            title,
            payment_systems,
            telephone_number,
            card_number,
            ft.Row(spacing=5, alignment=ft.MainAxisAlignment.CENTER,
                   controls=[expiry_date, CVV_password]),
            alert_message,
            ft.Row(alignment=ft.MainAxisAlignment.CENTER, controls=[
                   back_btn, MOBILEMONEY_payment, MPESA_payment, CARD_payment]),
            ft.Divider(),
        ],
    )

    payment_sheet = ft.BottomSheet(
        content=ft.Container(
            width=300,
            content=details
        )
    )

    page.show_dialog(payment_sheet)
