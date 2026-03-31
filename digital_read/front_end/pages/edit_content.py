import flet as ft
import requests
import boto3
import mimetypes

async def edit_content(page, navigate, content_id, title, theme, level, description, access_type, cover_path, content_type):

    #get token from client storage... pass then in the requests header
    client_token =  await page.shared_preferences.get("digital_read_user_token")
    
    #if no token go to login
    if not client_token:
        message.value="Login First"
        page.run_task(navigate, "/login")
        return None


    async def logic(e):
        submit_btn.disabled = True
        try:
            #send the login details to the server to be validated
            response = requests.post("http://127.0.0.1:8080/validate_upload_edit",
                                    json={
                                        "token":client_token,
                                        "title":title.value,
                                        "theme":theme.value,
                                        "level":level.value,
                                        "description":description.value,
                                        "access_type": access_type.selected[0] if access_type.selected else None, #pick the item selected from the segmented button
                                        "cover_photo":stored_cover.name if stored_cover else cover_path, #get it from the variable storing the picked file object
                                        "upload_type":content_type,
                                        })
            
            res = response.status_code #get response
            UUID_cover_name  = response.json().get("UUID_cover_name") #get UUID_cover_name 

            #file received then upload to wasabi and save to db
            if res == 200:
                submit_btn.disabled = True
                message.color = ft.Colors.BLUE_600
                message.value = "Uploading files..."
                data = response.json() #get the feedback from backend
                           
                finalize = requests.post("http://127.0.0.1:8080/update_content",
                    json={
                        "token":client_token,
                        "content_id":content_id,
                        "title":title.value,
                        "theme":theme.value,
                        "level":level.value,
                        "description":description.value,
                        "access_type": access_type.selected[0] if access_type.selected else None, #pick the item selected from the segmented button 
                        "cover_photo":UUID_cover_name,
                                                    "upload_type":content_type,
                                            })
                                
                if finalize.status_code == 200:
                                    submit_btn.disabled = True
                                    message.color = ft.Colors.GREEN_700
                                    message.value="Upload successful!"
                                    #navigate to documents page
                                    page.run_task(navigate,"/documents")
                                    return None
                            
                elif finalize.status_code == 400:
                                    submit_btn.disabled = False
                                    message.color = ft.Colors.RED_600
                                    message.value="Missing required details!"

                elif finalize.status_code == 401:
                                    submit_btn.disabled = False
                                    message.color = ft.Colors.RED_600
                                    message.value="Token invalid or expired!"
                                    page.run_task(navigate,"/login")
                                    return None
                                
                elif finalize.status_code == 500:
                                    submit_btn.disabled = False
                                    message.color = ft.Colors.RED_600
                                    message.value="Server error during finalizing upload!"

                else:
                                    submit_btn.disabled = False
                                    message.color = ft.Colors.RED_600
                                    message.value="An unknown error occured during finalizing upload!"

#______continue with responses from backend________________----------
            elif res == 401:
                submit_btn.disabled = False
                message.value = "Missing token!"
                page.run_task(navigate, "/login")
                return None
            
            elif res == 400:
                submit_btn.disabled = False
                message.value="Missing required fields!"
            elif res == 406:
                submit_btn.disabled = False
                message.value="Invalid cover image format!"
            elif res == 422:
                submit_btn.disabled = False
                message.value="Invalid document format!"
            elif res == 500:
                submit_btn.disabled = False
                message.value="Server error during validation!"
            else:
                submit_btn.disabled = False
                message.value="An unknown error occured!"

        except Exception as e:
            submit_btn.disabled = False
            print(f"Internal server error: {e}")
            message.value="Internal server error"
            return None
            #close the app window

    #storing the picked file object by default list is empty
    stored_cover = None

    #cover photo picker
    #opens dialogue to get cover images
    
    file_picker = ft.FilePicker()#define document picker control it will manage opening and uploading documents_picker


    async def on_cover_pick(e):
        nonlocal stored_cover
        #submit_btn.disabled = False
        picked_cover = await file_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg"]
        )
        stored_cover = picked_cover[0] if picked_cover else None  #store the selected file in the stored_cover variable
        selected_cover_photo.value = stored_cover.name if stored_cover else cover_path #update the selected_document to show details about file selected or show the current path stored
    



    message = ft.Text(
        "", 
        color=ft.Colors.RED
        )

    title=ft.TextField(
        label="Ttilte",
        hint_text="Title",
        autofocus=True,
        value=title,
        )
    theme=ft.TextField(
        label="theme",
        hint_text="Subject",
        value=theme,
        )
    level=ft.TextField(
        label='level',
        hint_text="Education level",
        value=level,
        )
    description=ft.TextField(
        label="Description",
        hint_text="Something about your piece of work", 
        multiline=True, 
        max_lines=5,
        value=description,
        )
    access_type = ft.SegmentedButton(
        allow_empty_selection=False,
        allow_multiple_selection=False,
        selected=[f"{access_type}"],
        segments=[
            ft.Segment(value="free", label=ft.Text("Free"), opacity=0.5, tooltip="Available to all users",),
            ft.Segment(value="paid", label=ft.Icon(ft.icons.Icons.PAYMENTS), opacity=1.0, tooltip="Available to only premium users",),
        ]
    )
    cover_photo=ft.TextButton("cover photo", icon=ft.icons.Icons.CAMERA_ALT_ROUNDED, on_click=on_cover_pick)
    selected_cover_photo=ft.Text(f"{cover_path}", expand=True)

    upload_form = ft.Container(
        bgcolor=ft.Colors.WHITE,
        padding=24,
        border_radius=16,
        alignment=ft.Alignment.CENTER,
        width=360,
        shadow=ft.BoxShadow(
            blur_radius=15,
            color=ft.Colors.BLACK12,
            offset=ft.Offset(0, 4)
        ),

        content = ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
            controls=[
                ft.Text(
                    "Update Content", 
                    size=22, 
                    weight=ft.FontWeight.BOLD,
                    ),
                ft.Text("Share your knowledge with the world", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                title,
                theme,
                level,
                description,
                ft.Text("Select New Access type", size=14, weight=ft.FontWeight.W_600),
                access_type,
                ft.Row(controls=[cover_photo, selected_cover_photo]),
                message,
                ft.Row(
                    spacing=16,
                    controls=[
                        ft.Button("Back", expand=True, icon=ft.Icons.ARROW_BACK, icon_color=ft.Colors.GREEN_600, on_click=lambda e: page.run_task(navigate,"/account")), #go back to documents
                        submit_btn := ft.Button("Update",expand=True, bgcolor=ft.Colors.BLUE_500, color=ft.Colors.WHITE, icon=ft.icons.Icons.UPLOAD,  on_click=logic), #call the logic function to handle upload 
                    ]
                ),
            ]
        )
    )

    return ft.View(
        route="/edit_content",
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.GREY_100,
                content=upload_form #call the upload form
            )
        ]
    )


