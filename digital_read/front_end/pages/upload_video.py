import flet as ft
import requests
import mimetypes


async def upload_video(page, navigate):

    # get token from client storage... pass then in the requests header
    client_token = await page.shared_preferences.get("digital_read_user_token")
    content_type = "VIDEO"
    media_uuid_holder = {"value": None}

    # if no token go to login
    if not client_token:
        message.value = "Login First"
        page.run_task(navigate, "/login")
        return None


# function to send response to backend validate cover
    def validate_cover(cover_name):
        try:
            res = requests.post("http://127.0.0.1:8080/validate_cover",
                                json={
                                    "token": client_token,
                                    "cover_photo": cover_name,
                                    "upload_type": content_type,
                                })

            if res.status_code == 200:
                # read response to get uuid_cover
                urls = res.json()
                UUID_cover_name = urls["UUID_cover_name"]

                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.BLUE_600
                message.value = "Cover photo is valid!"
                return {"UUID_cover_name": UUID_cover_name}

            elif res.status_code == 401:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Token invalid or expired!"
                page.run_task(navigate, "/login")
                return None
            elif res.status_code == 400:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Missing cover photo!"
                return False
            elif res.status_code == 422:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Missing or invalid upload type!"
                return False
            elif res.status_code == 406:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Invalid cover image format!"
                return False
            elif res.status_code == 500:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Server error during cover validation!"
                return False
            else:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "An unknown error occured during cover validation!"
                return False
        except Exception as e:
            submit_btn.disabled = False
            print(f"Internal server error during cover validation: {e}")
            message.visible = True
            message.value = "Internal server error during cover validation"
            return False
  
    # function to send request to backend to validate content file
    def validate_content(media_name):
        try:
            res = requests.post("http://127.0.0.1:8080/validate_content",
                                json={
                                    "token": client_token,
                                    "title": title.value,
                                    "theme": theme.value,
                                    "level": level.value,
                                    "description": description.value,
                                    "access_type": access_type.selected[0] if access_type.selected else None,
                                    "upload_type": content_type,
                                    "media": media_name
                                })
            if res.status_code == 200:
                # read response to get uuid_cover
                urls = res.json()
                UUID_video_name = urls["UUID_video_name"]

                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.BLUE_600
                message.value = "Upload is valid!"
                return {"UUID_video_name": UUID_video_name}

            elif res.status_code == 401:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Token invalid or expired!"
                page.run_task(navigate, "/login")
                return None

            elif res.status_code == 400:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Missing media file!"
                return False
            elif res.status_code == 422:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Missing or invalid metadata fields!"
                return False
            elif res.status_code == 406:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Invalid media file format!"
                return False
            elif res.status_code == 500:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Server error during media validation!"
                return False
            else:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "An unknown error occured during media validation!"
                return False
        except Exception as e:
            submit_btn.disabled = False
            print(f"Internal server error during media validation: {e}")
            message.visible = True
            message.value = "Internal server error during media validation"
            return False


    # function to generate-upload-urls for either cover or media, when called
    def generate_cloud_urls(media_uuid_name):
        try:
            res = requests.post("http://127.0.0.1:8080/generate-upload-urls",
                                json={
                                    "token": client_token,
                                    "media_uuid_name": media_uuid_name
                                })
            # read the media_upload_url from the response
            urls = res.json()
            media_url = urls["media_url"]

            if res.status_code == 200:
                return media_url
            else:
                return None
        except Exception as e:
            print(f"Internal server error during generating upload url: {e}")
            return None


    # function to upload the passed file or cover to the cloud
    async def upload_to_cloud(file_picker, file_obj, upload_url):
        try:
            await file_picker.upload([
                ft.FilePickerUploadFile(
                    name=file_obj.name,
                    upload_url=upload_url,
                    method="PUT"
                ),
            ])
            return True
        except Exception as e:
            print("Upload error:", e)
            return False

    # function to save the cover
    def save_cover(UUID_cover_name, media_uuid_name):
        try:
            res = requests.post("http://127.0.0.1:8080/save_cover_pic",
                                json={
                                    "token": client_token,
                                    "cover_photo": UUID_cover_name,
                                    "upload_type": content_type,
                                    "media": media_uuid_name
                                })
            if res.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error saving cover details to database: {e}")
            return False
    
    # function to save the media file

    def save_media(uuid_file_path):
        try:
            res = requests.post("http://127.0.0.1:8080/save_content",
                                json={
                                    "token": client_token,
                                    "title": title.value,
                                    "theme": theme.value,
                                    "level": level.value,
                                    "description": description.value,
                                    "access_type": access_type.selected[0] if access_type.selected else None,
                                    "file_path": uuid_file_path,
                                    "upload_type": content_type
                                })
            if res.status_code == 200:
                return True
            else:
                return False
        except Exception as e:
            print(f"Error saving media details to database: {e}")
            return False
    
    async def cover_photo_logic(e):
        try:
            # get the media_uuid name from the list where we saved it
            media_uuid_name = media_uuid_holder["value"]

            # alert me me media uuid name is missing
            if not media_uuid_name:
                print("Media UUID missing!")
                return None

            # validate that the user has actually selected a cover photo before proceeding with the upload since the cover photo is optional we can show error message prompting user to select cover photo but still allow them to proceed with the upload without cover photo if they choose to ignore the message and go back to documents page or if they click the ignore button for cover upload after successful content upload
            if not stored_cover:
                message.value = "Select a cover photo first!"
                message.visible = True
                return None

            cover_validation_response = validate_cover(
                cover_name=stored_cover.name)
            # if cover is valid then generate uuid name for the cover
            if cover_validation_response:
                cover_uuid_name = cover_validation_response.get(
                    "UUID_cover_name")
                cover_url = generate_cloud_urls(cover_uuid_name)
                # get the cover upload url from the response
                if cover_url:
                    upload_success = await upload_to_cloud(
                        cover_picker,
                        stored_cover,
                        cover_url
                    )
                    verify_upload_response = requests.post(
                        "http://127.0.0.1:8080/verify-upload", json={
                            "uploaded_name": cover_uuid_name,
                            "token": client_token
                        })
                    # upload the file to the cloud using the generated url
                    if upload_success == True and verify_upload_response.status_code == 200:
                        save_cover_database = save_cover(
                            UUID_cover_name=cover_uuid_name, media_uuid_name=media_uuid_name)
                        # save the generated url and other details to the database
                        if save_cover_database:
                            submit_btn.disabled = True
                            message.visible = True
                            message.color = ft.Colors.GREEN_700
                            message.value = "Cover photo uploaded successfully!"
                            page.run_task(navigate, "/documents")
                            return None
                        # if failed to save to database show error message
                        else:
                            submit_btn.disabled = False
                            message.visible = True
                            message.color = ft.Colors.RED_600
                            message.value = "Failed to save cover photo details to database!"
                            return None
                    # if failed to upload to cloud show error message
                    else:
                        submit_btn.disabled = False
                        message.visible = True
                        message.color = ft.Colors.RED_600
                        message.value = "Failed to upload cover photo to cloud!"
                        return None
                # if failed to get the upload url show error message
                else:
                    submit_btn.disabled = False
                    message.visible = True
                    message.color = ft.Colors.RED_600
                    message.value = "Cover photo validation failed during upload!"
                    return None
            elif cover_validation_response is False:
                submit_btn.disabled = False
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Cover photo validation failed during upload!"
                return None
        except Exception as e:
            print(
                f"Internal server error during cover photo upload logic: {e}")
            return None

    # upload logic
    async def upload_logic():
        try:
            # validate the content file first before anything else since its mandatory and if it fails validation we can show error message without going through the rest of the process
            if not stored_media:
                message.visible = True
                message.color = ft.Colors.RED_600
                message.value = "Select a video first!"
                return None

            # when the stored media exists
            else:
                # validate the content file with backend and get the uuid name for the file if validation is successful, this uuid name will be used to generate the upload url and also will be stored in the database as reference to the actual file in cloud storage
                validation_response = validate_content(
                    media_name=stored_media.name)

                # if validation fails show error message
                if not validation_response:
                    message.visible = True
                    message.color = ft.Colors.RED_600
                    message.value = "Video validation failed!"
                    return None

                else:
                    # if validation is successful get the generated uuid name for the content file from the response
                    media_uuid_name = validation_response.get(
                        "UUID_video_name")

                    # store uuid for cover logic
                    media_uuid_holder["value"] = media_uuid_name

                    media_url = generate_cloud_urls(media_uuid_name)
                    # get the media upload url from the response
                    if media_url:
                        upload_success = await upload_to_cloud(
                            content_picker,
                            stored_media,
                            media_url
                        )
                        # upload the file to the cloud using the generated url
                        # add the upload verify logic here to check if the media is successfully uploaded and available in the cloud storage before saving the details to database, this is to avoid saving details to database when the upload actually failed but the cloud upload api returned success response
                        verify_upload_response = requests.post(
                            "http://127.0.0.1:8080/verify-upload", json={
                                "uploaded_name": media_uuid_name,
                                "token": client_token
                            })
                        if upload_success == True and verify_upload_response.status_code == 200:
                            save_media_database = save_media(
                                uuid_file_path=media_uuid_name)
                            # save the generated url and other details to the database
                            if save_media_database:
                                submit_btn.disabled = True
                                message.visible = True
                                message.color = ft.Colors.GREEN_700
                                message.value = "Upload successful!"

                                # make all the other controls invisible except the message and show the cover photo and the options to either upload the cover or ignore and go back to documents page
                                # change the welcome text to prompt user to upload cover photo
                                welcome_text.value = "Add a cover photo to make your video more attractive!"
                                title.visible = False
                                theme.visible = False
                                level.visible = False
                                description.visible = False
                                access_type_text.visible = False
                                access_type.visible = False
                                cancel_btn.visible = False
                                submit_btn.visible = False
                                cover_photo.visible = True
                                selected_cover_photo.visible = True
                                ignore_cover_upload.visible = True
                                upload_cover_btn.visible = True

                                return None
                            # if failed to save to database show error message
                            else:
                                submit_btn.disabled = False
                                message.visible = True
                                message.color = ft.Colors.RED_600
                                message.value = "Failed to save upload details to database!"
                                return None
                        # if failed to upload to cloud show error message
                        else:
                            submit_btn.disabled = False
                            message.visible = True
                            message.color = ft.Colors.RED_600
                            message.value = "File upload to cloud failed!"
                            return None
                    # if failed to get the upload url show error message
                    else:
                        submit_btn.disabled = False
                        message.visible = True
                        message.color = ft.Colors.RED_600
                        message.value = "File validation failed during upload!"
                        return None
        except Exception as e:
            submit_btn.disabled = False
            print(f"Internal server error during upload logic: {e}")
            message.visible = True
            message.value = "Internal server error during upload"
            return None    
   



#######################################################################################################
     # function that saves the generated urls and other details to the database
    # save files details to database
    def save_to_database(
            UUID_cover_name,
            UUID_video_name
    ):
        submit_btn.disabled = True
        finalize = requests.post("http://127.0.0.1:8080/save_upload",
                                 json={
                                     "token": client_token,
                                     "title": title.value,
                                     "theme": theme.value,
                                     "level": level.value,
                                     "description": description.value,
                                     # pick the item selected from the segmented button
                                     "access_type": access_type.selected[0] if access_type.selected else None,
                                     "cover_photo": UUID_cover_name,
                                     "media": UUID_video_name,
                                     "upload_type": content_type,
                                 })

        if finalize.status_code == 200:
            submit_btn.disabled = True
            message.color = ft.Colors.GREEN_700
            message.value = "Upload successful!"
            # navigate to documents page
            page.run_task(navigate, "/documents")
            return None

        elif finalize.status_code == 400:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Missing required details!"
            return None

        elif finalize.status_code == 401:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Token invalid or expired!"
            page.run_task(navigate, "/login")
            return None

        elif finalize.status_code == 409:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Either cover or file is missing!"
            print("Either cover or file is missing!")
            return None

        elif finalize.status_code == 500:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Server error during finalizing upload!"

        else:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "An unknown error occured during finalizing upload!"
        # end of save save to db

    # function that uploads content to wasabi cloud storage

    async def upload_files_to_wasabi(
        cover_picker,
        content_picker,
        stored_cover,
        stored_media,
        cover_uuid_name,
        media_uuid_name,
        token=client_token,
    ):

        submit_btn.disabled = True
        # get the content type for cover and media.. azn the extension
        cover_type, _ = mimetypes.guess_type(stored_cover.name)
        media_type, _ = mimetypes.guess_type(stored_media.name)

        # fallback safety
        cover_type = cover_type or "application/octet-stream"
        media_type = media_type or "application/octet-stream"

        # 1️⃣ Request presigned URLs from backend
        res = requests.post(
            "http://127.0.0.1:8080/generate-upload-urls",
            json={
                "token": token,
                "cover_name": cover_uuid_name,
                "media_name": media_uuid_name,
                "cover_type": cover_type,
                "media_type": media_type
            }
        )

        if res.status_code == 200:
            urls = res.json()

            cover_url = urls["cover_upload_url"]
            media_url = urls["media_upload_url"]

            # 2️⃣ Upload cover + media using FilePickerUpload
            await cover_picker.upload([
                ft.FilePickerUploadFile(
                    name=cover_uuid_name,
                    upload_url=cover_url,
                    method="PUT"
                ),
                ft.FilePickerUploadFile(
                    name=stored_media.name,
                    upload_url=media_url,
                    method="PUT"
                )
            ]
            )

            # 2️⃣ Upload cover + media using FilePickerUpload
            await content_picker.upload([
                ft.FilePickerUploadFile(
                    name=content_picker,
                    upload_url=cover_url,
                    method="PUT"
                ),
                ft.FilePickerUploadFile(
                    name=stored_media.name,
                    upload_url=media_url,
                    method="PUT"
                )
            ]
            )

            # After file_picker.upload(...)
            verify = requests.post(
                "http://127.0.0.1:8080/verify-upload",
                json={
                    "token": token,
                    "cover_name": cover_uuid_name,
                    "media_name": media_uuid_name
                }
            )

            if verify.status_code == 200:
                print("Upload verified on Wasabi")
                return True
            else:
                print("Upload verification failed")
                return False

        elif res.status_code == 401:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Token invalid or expired!"
            page.run_task(navigate, "/login")
            return None

        elif res.status_code == 400:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Missing filenames"
            return None

        elif res.status_code == 500:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Could not generate presigned URLs"
            return None

        else:
            submit_btn.disabled = False
            message.color = ft.Colors.RED_600
            message.value = "Unknown error occured, could not upload files"
            page.run_task(navigate, "/documents")
            return None

            # end of function that uploads to wasabi cloud storage

    async def logic(e):
        submit_btn.disabled = True
        try:
            # send the login details to the server to be validated
            response = requests.post("http://127.0.0.1:8080/validate_upload",
                                     json={
                                         "token": client_token,
                                         "title": title.value,
                                         "theme": theme.value,
                                         "level": level.value,
                                         "description": description.value,
                                         # pick the item selected from the segmented button
                                         "access_type": access_type.selected[0] if access_type.selected else None,
                                         # get it from the variable storing the picked file object
                                         "cover_photo": stored_cover.name if stored_cover else None,
                                         # get it from the variable storing the picked file object
                                         "media": stored_media.name if stored_media else None,
                                         "upload_type": content_type,
                                     })

            res = response.status_code  # get response
            UUID_cover_name = response.json().get("UUID_cover_name")  # get UUID_cover_name
            UUID_video_name = response.json().get("UUID_video_name")  # get UUID_video_name

            # file received then upload to wasabi and save to db
            if res == 200:
                submit_btn.disabled = True
                message.color = ft.Colors.BLUE_600
                message.value = "Uploading files..."

                success = await upload_files_to_wasabi(
                    cover_picker,
                    content_picker,
                    stored_cover,
                    stored_media,
                    UUID_cover_name,
                    UUID_video_name
                )

                if success:
                    # function to save to database
                    save_to_database(
                        UUID_cover_name,
                        UUID_video_name
                    )
                else:
                    message.value = "Upload failed verification"
                    submit_btn.disabled = False

            # ______continue with responses from backend________________----------
            elif res == 401:
                submit_btn.disabled = False
                message.value = "Missing token!"
                page.run_task(navigate, "/login")
                return None

            elif res == 400:
                submit_btn.disabled = False
                message.value = "Missing required fields!"
            elif res == 406:
                submit_btn.disabled = False
                message.value = "Invalid cover image format!"
            elif res == 422:
                submit_btn.disabled = False
                message.value = "Invalid video format!"
            elif res == 500:
                submit_btn.disabled = False
                message.value = "Server error during validation!"
            else:
                submit_btn.disabled = False
                message.value = "An unknown error occured!"

        except Exception as e:
            submit_btn.disabled = False
            print(f"Internal server error: {e}")
            message.value = "Internal server error"
            return None
            # close the app window

    # storing the picked file object by default list is empty
    stored_cover = None
    stored_media = None

    # cover photo picker
    # opens dialogue to get cover images

    # video picker
    # opens dialogue to get videos
    # define video picker control it will manage opening and uploading videos_picker
    ######################################################################################################################

    cover_picker = ft.FilePicker()
    content_picker = ft.FilePicker()

    async def on_cover_pick(e):
        nonlocal stored_cover
        # submit_btn.disabled = False
        picked_cover = await cover_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=["png", "jpg", "jpeg"]
        )
        # store the selected file in the stored_cover variable
        stored_cover = picked_cover[0] if picked_cover else None
        # update the selected_video to show details about file selected or show message when not selected
        selected_cover_photo.value = stored_cover.name if stored_cover else None

    async def on_media_pick(e):
        nonlocal stored_media
        picked_media = await content_picker.pick_files(
            allow_multiple=False,
            allowed_extensions=['mp4', 'webm', 'mkv']
        )
        # store the selected file in the stored_media variable
        stored_media = picked_media[0] if picked_media else None
        # update the selected_video to show details about file selected or show message when not selected
        selected_video.value = stored_media.name if stored_media else None

    message = ft.Text(
        "",
        color=ft.Colors.RED
    )

    title = ft.TextField(
        hint_text="video title",
        autofocus=True
    )
    theme = ft.TextField(
        hint_text="Subject",
    )
    level = ft.TextField(
        hint_text="Education level",
    )
    description = ft.TextField(
        hint_text="Something about your piece of work",
        multiline=True,
        max_lines=5
    )
    access_type = ft.SegmentedButton(
        allow_empty_selection=False,
        allow_multiple_selection=False,
        selected=["free"],
        segments=[
            ft.Segment(value="free", label=ft.Text("Free"),
                       opacity=0.5, tooltip="Available to all users",),
            ft.Segment(value="paid", label=ft.Icon(ft.icons.Icons.PAYMENTS),
                       opacity=1.0, tooltip="Available to only premium users",),
        ]
    )
    cover_photo = ft.TextButton(
        "cover photo", icon=ft.icons.Icons.CAMERA_ALT_ROUNDED, on_click=on_cover_pick, visible=False)
    selected_cover_photo = ft.Text(
        "NO cover photo selected", expand=True, visible=False)


    video = ft.TextButton(
        "video", icon=ft.icons.Icons.DESCRIPTION, on_click=on_media_pick)
    selected_video = ft.Text("NO video selected", expand=True,)

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

        content=ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.ALWAYS,  # Enable page-level swipe scrolling
            controls=[
                ft.Text(
                    "Upload New Video",
                    size=22,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text("Share your knowledge with the world", size=14,
                        weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_600),
                title,
                theme,
                level,
                description,
                ft.Text("Select Video Access type", size=14,
                        weight=ft.FontWeight.W_600),
                access_type,
                ft.Row(controls=[cover_photo, selected_cover_photo]),
                ft.Row(controls=[video, selected_video]),
                message,
                ft.Row(
                    spacing=16,
                    controls=[
                        cancel_btn := ft.Button("Cancel", expand=True, icon=ft.Icons.CANCEL, on_click=lambda e: page.run_task(
                            navigate, "/videos")),  # go back to documents
                        # call the logic function to handle upload
                        submit_btn := ft.Button("Upload", expand=True, bgcolor=ft.Colors.BLUE_500,
                                                color=ft.Colors.WHITE, icon=ft.icons.Icons.UPLOAD,  on_click=upload_logic),
                        # buttons for uploading or ignoring cover are invisble until the content file uploads successfully then they become visible
                        ignore_cover_upload := ft.Button("ignore", expand=True, icon=ft.Icons.CANCEL, visible=False, on_click=lambda e: page.run_task(
                            navigate, "/videos")),  # go back to documents
                        upload_cover_btn := ft.Button("Cover", expand=True, bgcolor=ft.Colors.BLUE_500, visible=False,
                                                      color=ft.Colors.WHITE, icon=ft.icons.Icons.UPLOAD, on_click=cover_photo_logic)
                    ]
                ),
            ]
        )
    )

    return ft.View(
        route="/upload_video",
        controls=[
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                bgcolor=ft.Colors.GREY_100,
                content=upload_form  # call the upload form
            )
        ]
    )
