import sqlite3
from sqlite3 import Error
import uuid
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self, db_file="digital_read.db"):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            # THIS IS THE MAGIC LINE: It makes results act like Dictionaries
            self.conn.row_factory = sqlite3.Row

            # uncomment to reactivate or recreate these tables if database was cleared
            self.user_table()
            self.sessions_table()
            self.subscription_table()
            self.videos_table()
            self.podcasts_table()
            self.coins_wallet_table()
            self.points_wallet_table()
            self.documents_table()
            self.comments_table()
            self.likes_table()
            self.downloads_table()
            self.view_table()
            self.payments_table()
            self.temp_tokens_table()

        except Error as e:
            print(f"Error connecting to the database: {e}")

    # function for creating a new column
    def create_more_cloumns(self, new_column, table_name, data_type):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    f"""ALTER TABLE {table_name} ADD COLUMN {new_column} {data_type}  DEFAULT 0;""")
                print(
                    f"new cloumn: {new_column} has been added in table: {table_name}")
                self.conn.commit()
            except Error as e:
                print(
                    f"Error CREATING new column: {new_column} in table {table_name}...")


# ------------------------------------------------------SESSION TABLE-----------------------------------------------------------

# create sessions table


    def sessions_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS SESSIONS (
                        token TEXT PRIMARY KEY,
                        email TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print("Error creating SESSIONS table...")

    # add new session to database
    def token_gateway(self, token):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT email FROM SESSIONS WHERE token = ?",
                    (token,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get session: {e}")

    # add new session to database
    def add_session(self, email, token):
        if self.conn:
            try:
                sql = "INSERT INTO SESSIONS (email, token) VALUES (?,?)"
                cursor = self.conn.cursor()
                cursor.execute(sql, (email, token))
                self.conn.commit()
            except Error as e:
                print(f"Failed to add SESSION...{e}")

    # DELETE SESSION

    def delete_session(self, token):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM SESSIONS WHERE token=?", (token,))
            self.conn.commit()
            print("session deleted")

    # get session details
    def get_session_details(self, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM SESSIONS WHERE email = ?", (email,))
            result = cursor.fetchone()
            return dict(result) if result else None
        return None

# _______________________________________________________________temp_tokens_______________________________________________________________

# create sessions table
    def temp_tokens_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS TEMP_TOKENS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        token TEXT UNIQUE,
                        email TEXT,
                        content_type TEXT,
                        content_id INTEGER,
                        expires_at TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print("Error creating TEMP_TOKENS table...")

    # create temp token
    def create_temp_token(self, email, content_type, content_id):
        if self.conn:
            try:
                token = str(uuid.uuid4())
                # get current time + 2 minutes
                expires_at = datetime.utcnow() + timedelta(minutes=2)

                sql = "INSERT INTO TEMP_TOKENS (email, token, content_type, content_id, expires_at) VALUES (?,?,?,?,?)"
                cursor = self.conn.cursor()
                cursor.execute(
                    sql, (email, token, content_type, content_id, expires_at))
                self.conn.commit()
                return token
            except Error as e:
                print(f"Failed to add temp_token ...{e}")

    # function that will be used to validate token
    def validate_temp_token(self, token):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT email FROM TEMP_TOKENS WHERE token = ? AND expires_at > ?",
                    (token, datetime.utcnow())
                )

                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get temp_token: {e}")

    # get session details

    def delete_temp_token(self, token):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM TEMP_TOKENS WHERE token=?", (token,))
            self.conn.commit()
        return None


# ________________________________________________________________PAYMENTS________________________________________________________________


    def payments_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS PAYMENTS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tx_ref VARCHAR(100) UNIQUE NOT NULL,
                        flw_ref VARCHAR(100),
                        user_email VARCHAR(255) NOT NULL,
                        subscription_plan VARCHAR(100) NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        currency VARCHAR(10) DEFAULT 'UGX',
                        payment_method VARCHAR(50),
                        status VARCHAR(50) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating PAYMENTS table: {e}")

    def create_pending_payment(self, tx_ref, flw_ref, user_email, subscription_plan, amount, currency, payment_method, status):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                sql = """
                    INSERT INTO PAYMENTS (
                        tx_ref, flw_ref, user_email, subscription_plan, amount, currency, payment_method, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                cursor.execute(sql, (
                    tx_ref,
                    flw_ref,
                    user_email,
                    subscription_plan,
                    amount,
                    currency,
                    payment_method,
                    status
                ))
                self.conn.commit()
            except Error as e:
                print(f"Error creating pending payment: {e}")

    # checking a payment by email

    def payment_exists(self, tx_ref):
        """
        Checks if a payment already exists in the 'payments' table.
        Returns:
            bool: True if the payment exists, False otherwise.
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                # gets a payment with the matching email entered
                cursor.execute(
                    "SELECT * FROM PAYMENTS WHERE tx_ref = ?", (tx_ref,))
                # fetchone() will return a record (e.g., (1,)) if found, or None if not found.
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Database error during payment check: {e}")
                return False
        return False

    # get deatils about payment by tx_ref

    def get_payment_details(self, tx_ref):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM PAYMENTS WHERE tx_ref = ?", (tx_ref,))
            result = cursor.fetchone()
            return dict(result) if result else None
        return None

    # update payment

    def update_payment(self, new_status, tx_ref, flw_ref=None):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE PAYMENTS SET status=?, flw_ref=? WHERE tx_ref=?",
                           (new_status, flw_ref, tx_ref,))
            self.conn.commit()
            print("payment was successful updated")


# ----------------------------------------------------------- Subscriptions -------------------------------------------------------------

    # create SUBSCRIPTIONS table


    def subscription_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS SUBSCRIPTIONS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT NOT NULL UNIQUE,
                        subscription_plan TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating SUBSCRIPTION table: {e}")

    # checking a SUBSCRIPTION by email
    def user_subscribed(self, email):
        # add system to check duration according to plan. if past period, delete plan
        """
        Checks if an email subscription already exists in the 'subscription' table and the date still valid.
        Returns:
            bool: True if the subscription exists, False otherwise.
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                # gets a user with the matching email entered
                cursor.execute(
                    "SELECT 1 FROM SUBSCRIPTIONS WHERE email = ?", (email,))
                # fetchone() will return a record (e.g., (1,)) if found, or None if not found.
                return cursor.fetchone() is not None
            except Error as e:
                print(
                    f"Database error during email check for subscription: {e}")
                return False
        return False

    # add a subscription to database, thier, email, subscription_plan

    def subscribe(self, email, subscription_plan):
        if self.conn:
            try:
                sql = "INSERT INTO SUBSCRIPTIONS (email, subscription_plan) VALUES (?,?)"
                cursor = self.conn.cursor()
                cursor.execute(sql, (email, subscription_plan))
                self.conn.commit()
            except Error as e:
                print(f"Failed to subscribe: {e}")

    # get deatils about a subscription by email
    def subscription_details(self, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM SUBSCRIPTIONS WHERE email = ?", (email,))
            result = cursor.fetchone()
            return dict(result) if result else None
        return None

    # UNSUBSCRIPTION
    def unsubscribe(self, id, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM SUBSCRIPTIONS WHERE id=? and email=?", (id, email,))
            self.conn.commit()
            print("unsubscribed")


# ----------------------------------------------------------- USER TABLE -------------------------------------------------------------

    # create user table


    def user_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS USER (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        email TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL,
                        profile_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating USER table: {e}")

    # checking a user by email
    def email_exists(self, email):
        """
        Checks if an email already exists in the 'user' table.
        Returns:
            bool: True if the email exists, False otherwise.
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                # gets a user with the matching email entered
                cursor.execute("SELECT 1 FROM USER WHERE email = ?", (email,))
                # fetchone() will return a record (e.g., (1,)) if found, or None if not found.
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Database error during email check: {e}")
                return False
        return False

        # checking a user by username

    # check if user_nmae is already in use
    def username_exists(self, username):
        """
        Checks if an username already exists in the 'user' table.
        Returns:
            bool: True if the username exists, False otherwise.
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                # gets a user with the matching username entered
                cursor.execute(
                    "SELECT 1 FROM USER WHERE username = ?", (username,))
                # fetchone() will return a record (e.g., (1,)) if found, or None if not found.
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Database error during username check: {e}")
                return False
        return False

    # get username by email
    def get_username(self, email):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT username FROM USER WHERE email = ?",
                    (email,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get authur: {e}")

    # get user_id by email

    def get_user_id(self, email):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT id FROM USER WHERE email = ?",
                    (email,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get user_id: {e}")

    # add a user to database, thier username, email, hashed password, picture_path
    def add_user(self, username, email, password, profile_path):
        if self.conn:
            try:
                sql = "INSERT INTO USER (username, email, password, profile_path) VALUES (?,?,?,?)"
                cursor = self.conn.cursor()
                cursor.execute(sql, (username, email, password, profile_path))
                self.conn.commit()
            except Error as e:
                print(f"Failed to add user: {e}")

    # get deatils about a user by email
    def get_user_details(self, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM USER WHERE email = ?", (email,))
            result = cursor.fetchone()
            return dict(result) if result else None
        return None

    # update profie

    def update_profile(self, username, password, profile_path):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE USER SET username=?, password=?, profile_path=? WHERE id=?",
                           (username, password, profile_path,))
            self.conn.commit()
            print("Profile updated")

    # delete user
    def delete_user(self, user_id):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM USER WHERE id=?", (user_id,))
            self.conn.commit()
            print("user deleted")


# ----------------------------------------------------------- VIDEOS TABLE -------------------------------------------------------------

    # create videos table


    def videos_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS VIDEOS (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            theme TEXT NOT NULL,
                            level TEXT NOT NULL,
                            description TEXT NOT NULL,
                            cover_path TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            email TEXT NOT NULL,
                            authur TEXT NOT NULL,
                            access_type TEXT NOT NULL DEFAULT 'FREE',
                            likes_count INTEGER DEFAULT 0,
                            views_count INTEGER DEFAULT 0,
                            downloads_count INTEGER DEFAULT 0,
                            comments_count INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (authur) REFERENCES USER(username)
                               );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating VIDEOS table: {e}")

    # add new video
    def add_video(self, title, theme, level, description, cover_path, file_path, email, authur, access_type):
        if self.conn:
            try:
                sql = """INSERT INTO VIDEOS (title, theme, level, description, cover_path, file_path, email, authur, access_type)
                         VALUES (?,?,?,?,?,?,?,?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (title, theme, level, description,
                               cover_path, file_path, email, authur, access_type))
                self.conn.commit()
                print(f"video added {file_path}")
            except Error as e:
                print(f"Failed to add video: {e}")

    # get video details
    def get_all_videos(self, limit_count):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM VIDEOS ORDER BY RANDOM() LIMIT ?", (limit_count,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # get all videos by authur
    def get_all_videos_by_email(self, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM VIDEOS WHERE email = ?", (email,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # get video authur
    def video_authur(self, video_id):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT authur FROM VIDEOS WHERE id = ?",
                    (video_id,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get authur: {e}")

    # get single video by id for viewing

    def one_video(self, video_id):
        if not self.conn:
            return None
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM VIDEOS WHERE id = ?", (video_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)  # ✅ single document as dict

    # delete video

    def delete_video(self, video_id, authur):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM VIDEOS WHERE id=? and authur=?", (video_id, authur,))
            self.conn.commit()
            print("video deleted")


# ----------------------------------------------------------- PODCASTS TABLE -------------------------------------------------------------

    # create podcast table


    def podcasts_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS PODCASTS (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            theme TEXT NOT NULL,
                            level TEXT NOT NULL,
                            description TEXT NOT NULL,
                            cover_path TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            email TEXT NOT NULL,
                            authur TEXT NOT NULL,
                            access_type TEXT NOT NULL DEFAULT 'FREE',
                            likes_count INTEGER DEFAULT 0,
                            views_count INTEGER DEFAULT 0,
                            downloads_count INTEGER DEFAULT 0,
                            comments_count INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (authur) REFERENCES USER(authur)
                               );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating PODCASTS table: {e}")

    # add new podcast
    def add_podcast(self, title, theme, level, description, cover_path, file_path, email, authur, access_type):
        if self.conn:
            try:
                sql = """INSERT INTO PODCASTS (title, theme, level, description, cover_path, file_path, email, authur, access_type)
                         VALUES (?,?,?,?,?,?,?,?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (title, theme, level, description,
                               cover_path, file_path, email, authur, access_type))
                self.conn.commit()
                print(f"podcast added {file_path}")
            except Error as e:
                print(f"Failed to add podcast: {e}")

    # get podcast details
    def get_all_podcasts(self, limit_count):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM PODCASTS ORDER BY RANDOM() LIMIT ?", (limit_count,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # get PODCAST authur
    def podcast_authur(self, podcast_id):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT authur FROM PODCASTS WHERE id = ?",
                    (podcast_id,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get authur: {e}")

    # get all podcasts by authur

    def get_all_podcasts_by_email(self, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM PODCASTS WHERE email = ?", (email,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # get single document by id for viewing

    def one_podcast(self, podcast_id):
        if not self.conn:
            return None
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM PODCASTS WHERE id = ?", (podcast_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)  # ✅ single document as dict

    # update podcst
    def update_podcast(self, title, theme, level, description, cover_path, file_path, authur, access_type, podcast_id):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE PODCASTS SET title=?, theme=?, level=?, description=?, cover_path=?, file_path=?, authur=?, access_type=? WHERE id=?",
                           (title, theme, level, description, cover_path, file_path, authur, access_type, podcast_id,))
            self.conn.commit()
            print("podcast updated")

    # delete podcast
    def delete_podcast(self, podcast_id, authur):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM PODCASTS WHERE id=? and authur=?", (podcast_id, authur,))
            self.conn.commit()
            print("podcast deleted")


# ----------------------------------------------------------- DOCUMENT TABLE -------------------------------------------------------------

    # create document table


    def documents_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS DOCUMENTS (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            theme TEXT NOT NULL,
                            level TEXT NOT NULL,
                            description TEXT NOT NULL,
                            cover_path TEXT NOT NULL,
                            file_path TEXT NOT NULL,
                            email TEXT NOT NULL,
                            authur TEXT NOT NULL,
                            access_type TEXT NOT NULL DEFAULT 'FREE',
                            likes_count INTEGER DEFAULT 0,
                            views_count INTEGER DEFAULT 0,
                            downloads_count INTEGER DEFAULT 0,
                            comments_count INTEGER DEFAULT 0,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (authur) REFERENCES USER(authur)
                               );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating DOCUMENTS table: {e}")

    # add new document
    def add_document(self, title, theme, level, description, cover_path, file_path, email, authur, access_type):
        if self.conn:
            try:
                sql = """INSERT INTO DOCUMENTS (title, theme, level, description, cover_path, file_path, email, authur, access_type)
                         VALUES (?,?,?,?,?,?,?,?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (title, theme, level, description,
                               cover_path, file_path, email, authur, access_type))
                self.conn.commit()
                print(f"document added {file_path}")
            except Error as e:
                print(f"Failed to add document: {e}")

    # get document details
    def get_all_documents(self, limit_count):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM DOCUMENTS ORDER BY RANDOM() LIMIT ?", (limit_count,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # get DOCUMENT authur
    def document_authur(self, document_id):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT authur FROM DOCUMENTS WHERE id = ?",
                    (document_id,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
            except Error as e:
                print(f"Failed to get authur: {e}")

    # get all documents by authur

    def get_all_documents_by_email(self, email):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM DOCUMENTS WHERE email = ?", (email,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # get single document by id for viewing
    def one_document(self, document_id):
        if not self.conn:
            return None
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM DOCUMENTS WHERE id = ?", (document_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return dict(row)  # ✅ single document as dict

    # update podcst

    def update_document(self, title, theme, level, description, cover_path, file_path, authur, access_type, document_id):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("UPDATE DOCUMENTS SET title=?, theme=?, level=?, description=?, cover_path=?, file_path=?, authur=?, access_type=? WHERE id=?",
                           (title, theme, level, description, cover_path, file_path, authur, access_type, document_id,))
            self.conn.commit()
            print("document updated")

    # delete document
    def delete_document(self, document_id, authur):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM DOCUMENTS WHERE id=? and authur=?", (document_id, authur,))
            self.conn.commit()
            print("document deleted")


################################################################################################################################################################
# _________________________________________________---------------------------COMMENTS ON ALL MEDIA_________________________-----------------


    def comments_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS COMMENTS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        comments TEXT,
                        person_id INTEGER,
                        username TEXT,
                        content_id INTEGER,
                        content_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id) REFERENCES DOCUMENTS(id)
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating COMMENTS table: {e}")

    # add new comment
    def add_comment(self, person_id, content_id, comments, content_type, username):
        if self.conn:
            try:
                sql = """INSERT INTO COMMENTS (person_id, content_id, comments, content_type, username)
                         VALUES (?,?,?,?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (person_id, content_id,
                               comments, content_type, username))
                if content_type == "DOCUMENT":
                    cursor.execute(
                        "UPDATE DOCUMENTS SET comments_count = comments_count + 1 WHERE id=?", (content_id,))
                    print(f"document content liked")
                elif content_type == "PODCAST":
                    cursor.execute(
                        "UPDATE PODCASTS SET comments_count = comments_count + 1 WHERE id=?", (content_id,))
                    print(f"podcast content liked")
                elif content_type == "VIDEO":
                    cursor.execute(
                        "UPDATE VIDEOS SET comments_count = comments_count + 1 WHERE id=?", (content_id,))
                    print(f"commented on video")
                self.conn.commit()
                print("comment added")
            except Error as e:
                print(f"Failed to add comment: {e}")

    # get comments details
    def get_comments(self, content_id, content_type):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT * FROM COMMENTS WHERE content_id=? and content_type=?", (content_id, content_type,))
            rows = cursor.fetchall()
            # Convert all rows to list of dictionaries
            return [dict(row) for row in rows]
        return []

    # delete comment
    def delete_comment(self, person_id, content_id, comment_id, content_type):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM COMMENTS WHERE id=? AND content_id=? and person_id=? AND content_type=?",
                           (comment_id, content_id, person_id, content_type,))
            if content_type == "DOCUMENT":
                cursor.execute(
                    "UPDATE DOCUMENTS SET comments_count = comments_count - 1 WHERE id=?", (content_id,))
                print(f"document content liked")
            elif content_type == "PODCAST":
                cursor.execute(
                    "UPDATE PODCASTS SET comments_count = comments_count - 1 WHERE id=?", (content_id,))
                print(f"podcast content liked")
            elif content_type == "VIDEO":
                cursor.execute(
                    "UPDATE VIDEOS SET comments_count = comments_count - 1 WHERE id=?", (content_id,))
                print(f"commented on video")
            self.conn.commit()
            print("comment deleted")


# -------------------------------------------------------------Media likes-----------------------------------------------

    def likes_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS LIKES (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER,
                        user_id INTEGER,
                        posted_by TEXT,
                        content_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (content_id) REFERENCES DOCUMENTS(id)
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating  LIKES table: {e}")

    # checking a if user liked already
    def liked_already(self, content_id, user_id, content_type):
        """
        Checks if a row with user_id and content_id and content_type already table.
        Returns:
            bool: True if the exists, False otherwise.
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM LIKES WHERE content_id=? and user_id=? and content_type=?",
                               (content_id, user_id, content_type,))  # gets a u with the matching user_id entered
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Error during like check: {e}")
                return False
        return False

    # content liked
    def content_liked(self, content_id, user_id, content_type):
        if self.conn:
            try:
                sql = """INSERT INTO LIKES (content_id, user_id, content_type) 
                         VALUES (?,?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (content_id, user_id, content_type,))
                if content_type == "DOCUMENT":
                    cursor.execute(
                        "UPDATE DOCUMENTS SET likes_count = likes_count + 1 WHERE id=?", (content_id,))
                    print(f"document content liked")
                elif content_type == "PODCAST":
                    cursor.execute(
                        "UPDATE PODCASTS SET likes_count = likes_count + 1 WHERE id=?", (content_id,))
                    print(f"podcast content liked")
                elif content_type == "VIDEO":
                    cursor.execute(
                        "UPDATE VIDEOS SET likes_count = likes_count + 1 WHERE id=?", (content_id,))
                    print(f"video content liked")
                self.conn.commit()
            except Error as e:
                print(f"Failed to like content: {e}")

    # content unliked
    def content_unlike(self, content_id, user_id, content_type):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM LIKES WHERE content_id=? AND user_id=? AND content_type=?",
                               (content_id, user_id, content_type,))

                if content_type == "DOCUMENT":
                    cursor.execute(
                        "UPDATE DOCUMENTS SET likes_count = likes_count - 1 WHERE id=?", (content_id,))
                    print(f"document content unliked")
                elif content_type == "PODCAST":
                    cursor.execute(
                        "UPDATE PODCASTS SET likes_count = likes_count - 1 WHERE id=?", (content_id,))
                    print(f"podcast content unliked")
                elif content_type == "VIDEO":
                    cursor.execute(
                        "UPDATE VIDEOS SET likes_count = likes_count - 1 WHERE id=?", (content_id,))
                    print(f"video content unliked")
                self.conn.commit()
            except Exception as e:
                print(f"Error on unliking: {e}")

    # remove_likes_for_removed_conent

    def remove_likes_for_removed_conent(self, content_id, content_type):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM LIKES WHERE content_id=? AND content_type=?", (content_id, content_type,))
            self.conn.commit()
            print("all likes removed for this media")

    def count_document_likes(self, content_id, content_type):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM LIKES WHERE content_id=? AND content_type=?", (content_id, content_type,))
            return cursor.fetchone()[0]


# -------------------------------------------------------------content downloads--------------------------------------------

    def downloads_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS DOWNLOADS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER,
                        person_id INTEGER,
                        posted_by TEXT,
                        content_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id) REFERENCES DOCUMENTS(id)
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating  DOWNLOADS table: {e}")

    # download content
    def download_content(self, person_id, content_id, content_type):
        if self.conn:
            try:
                sql = """INSERT INTO DOWNLOADS (person_id, content_id, content_type) 
                         VALUES (?,?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (person_id, content_id, content_type))
                if content_type == "DOCUMENT":
                    cursor.execute(
                        "UPDATE DOCUMENTS SET downloads_count = downloads_count + 1 WHERE id=?", (content_id,))
                    print(f"document content liked")
                elif content_type == "PODCAST":
                    cursor.execute(
                        "UPDATE PODCASTS SET downloads_count = downloads_count + 1 WHERE id=?", (content_id,))
                    print(f"podcast content liked")
                elif content_type == "VIDEO":
                    cursor.execute(
                        "UPDATE VIDEOS SET downloads_count = downloads_count + 1 WHERE id=?", (content_id,))
                    print(f"video content downloaded")
                self.conn.commit()
                print(" content downloaded")
            except Error as e:
                print(f"Failed to download: {e}")

    # remove_download_for_removed_conent

    def remove_downloads_for_removed_conent(self, content_id, content_type):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM DOWNLOADS WHERE content_id=? AND content_type=?", (content_id, content_type,))
            self.conn.commit()
            print("all downloads removed for this media")

    # checking a if user liked already

    def downloaded_already(self, content_id, person_id, content_type):
        """
        Checks if a row with person_id and content_id and content_type already table.
        Returns:
            bool: True if the exists, False otherwise.
        """
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT * FROM DOWNLOADS WHERE content_id=? and person_id=? and content_type=?",
                               (content_id, person_id, content_type,))  # gets a u with the matching authur entered
                return cursor.fetchone() is not None
            except Error as e:
                print(f"Error during downloads check: {e}")
                return False
        return False

# ------------------------------------------------------------- views--------------------------------------------
    def view_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS VIEWS (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content_id INTEGER,
                        person_id INTEGER,
                        posted_by TEXT,
                        content_type TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (id) REFERENCES DOCUMENTS(id)
                    );
                """)
                self.conn.commit()
            except Error as e:
                print(f"Error creating VIEWS table: {e}")

    # add new comment
    def view_content(self, person_id, content_id, content_type):
        if self.conn:
            try:
                sql = """INSERT INTO VIEWS (person_id, content_id, content_type) 
                         VALUES (?,?)"""
                cursor = self.conn.cursor()
                cursor.execute(sql, (person_id, content_id, content_type))
                if content_type == "DOCUMENT":
                    cursor.execute(
                        "UPDATE DOCUMENTS SET views_count = views_count + 1 WHERE id=?", (content_id,))
                    print(f"document content liked")
                elif content_type == "PODCAST":
                    cursor.execute(
                        "UPDATE PODCASTS SET views_count = views_count + 1 WHERE id=?", (content_id,))
                    print(f"podcast content liked")
                elif content_type == "VIDEO":
                    cursor.execute(
                        "UPDATE VIDEOS SET views_count = views_count + 1 WHERE id=?", (content_id,))
                self.conn.commit()
                print(f"video content viewed")
            except Error as e:
                print(f"Failed to view: {e}")

    # remove_views_for_removed_conent

    def remove_views_for_removed_conent(self, content_id, content_type):
        if self.conn:
            cursor = self.conn.cursor()
            cursor.execute(
                "DELETE FROM VIEWS WHERE content_id=? AND content_type=?", (content_id, content_type,))
            self.conn.commit()
            print("all views removed for this media")


########################################################################################################################################
# ______________________________---------------------------------- general action on content_____________________________----------------------------

    # add new content
# _______________________________________________________________________________________________________________________________________________

    def add_content(self, title, theme, level, description, cover_path, file_path, email, authur, access_type, content_type):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                if content_type == "VIDEO":
                    sql = """INSERT INTO VIDEOS (title, theme, level, description, cover_path, file_path, email, authur, access_type) 
                         VALUES (?,?,?,?,?,?,?,?,?)"""
                    cursor.execute(sql, (title, theme, level, description,
                                         cover_path, file_path, email, authur, access_type))
                    self.conn.commit()
                    print(f"video added {file_path}")
                if content_type == "PODCAST":
                    sql = """INSERT INTO PODCASTS (title, theme, level, description, cover_path, file_path, email, authur, access_type) 
                         VALUES (?,?,?,?,?,?,?,?,?)"""
                    cursor.execute(sql, (title, theme, level, description,
                                         cover_path, file_path, email, authur, access_type))
                    self.conn.commit()
                    print(f"podcast added {file_path}")
                if content_type == "DOCUMENT":
                    sql = """INSERT INTO DOCUMENTS (title, theme, level, description, cover_path, file_path, email, authur, access_type) 
                         VALUES (?,?,?,?,?,?,?,?,?)"""
                    cursor.execute(sql, (title, theme, level, description,
                                         cover_path, file_path, email, authur, access_type))
                    self.conn.commit()
                    print(f"document added {file_path}")
            except Error as e:
                print(f"Failed to add video: {content_type}")
# ________________________________________________________________________________________________________________________________________________________
    # update content

    def update_content(self, content_type, title, theme, level, description, cover_path, access_type, content_id):
        if self.conn:
            print([content_type, title, theme, level, description,
                  cover_path, access_type, content_id])
            try:
                cursor = self.conn.cursor()
                if content_type == "VIDEO":
                    cursor.execute("UPDATE VIDEOS SET title=?, theme=?, level=?, description=?, cover_path=?, access_type=? WHERE id=?",
                                   (title, theme, level, description, cover_path, access_type, content_id,))
                    print("video updated")
                elif content_type == "PODCAST":
                    cursor.execute("UPDATE PODCASTS SET title=?, theme=?, level=?, description=?, cover_path=?, access_type=? WHERE id=?",
                                   (title, theme, level, description, cover_path, access_type, content_id,))
                    print("podcast updated")
                elif content_type == "DOCUMENT":
                    cursor.execute("UPDATE DOCUMENTS SET title=?, theme=?, level=?, description=?, cover_path=?, access_type=? WHERE id=?",
                                   (title, theme, level, description, cover_path, access_type, content_id,))
                    print("document updated")
                else:
                    print("content not updated")
                self.conn.commit()
            except Exception as e:
                print(f"error updating content {e}")


### _______________-------------------update the  cover photo only---------------______________###


    def update_save_cover(self, content_type, cover_path, file_path, email):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                if content_type == "VIDEO":
                    cursor.execute("UPDATE VIDEOS SET cover_path=? WHERE file_path=? AND email=?",
                                   (cover_path, file_path, email,))
                    print("video cover saved")
                elif content_type == "PODCAST":
                    cursor.execute("UPDATE PODCASTS SET cover_path=? WHERE file_path=? AND email=?",
                                   (cover_path, file_path, email,))
                    print("podcast cover saved")
                elif content_type == "DOCUMENT":
                    cursor.execute("UPDATE DOCUMENTS SET cover_path=? WHERE file_path=? AND email=?",
                                   (cover_path, file_path, email,))
                    print("document cover saved")
                else:
                    print("content not updated")
                self.conn.commit()
            except Exception as e:
                print(f"error updating content when adding cover {e}")

    # delete document

    def delete_content(self, content_id, email, content_type):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                if content_type == "DOCUMENT":
                    cursor.execute(
                        "DELETE FROM DOCUMENTS WHERE id=? and email=?", (content_id, email,))
                    print("document deleted")
                elif content_type == "VIDEO":
                    cursor.execute(
                        "DELETE FROM VIDEOS WHERE id=? and email=?", (content_id, email,))
                    print("video deleted")
                elif content_type == "PODCAST":
                    cursor.execute(
                        "DELETE FROM PODCASTS WHERE id=? and email=?", (content_id, email,))
                    print("podcast deleted")
                else:
                    print("failed to delelte media")
                self.conn.commit()
            except Exception as e:
                print(f"Error deleting media: {e}")


#############################################################################################################################################
# _______________________________________--------------------------POINTS___________ AND___________WALLETS____________________------------------------------------
# ------------------------------------------------------POINTS AND COINS TABLEs-----------------------------------------------------------

# create POINTS table

    def points_wallet_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS POINTS_WALLET (
                        id INTEGER PRIMARY KEY,
                        authur TEXT,
                        points_balance INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print("Error creating points_wallet table...")

    # add new points to database
    # pass the user id and points balance + reaction points
    def add_points(self, authur, reaction_points):
        if self.conn:
            try:
                cursor = self.conn.cursor()

                cursor.execute("""
                INSERT INTO POINTS_WALLET (authur, points_balance)
                VALUES (?, 0)
                """, (authur,))

                cursor.execute("""
                UPDATE POINTS_WALLET
                SET points_balance = points_balance + ?
                WHERE authur = ?
                """, (reaction_points, authur))
                self.conn.commit()
            except Error as e:
                print(f"Failed to add POINT...{e}")

    def get_points(self, authur):
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
            SELECT points_balance FROM POINTS_WALLET
            WHERE authur = ?
            """, (authur,))

            row = cursor.fetchone()

            return row["points_balance"] if row else 0
        except Error as e:
            print(f"Failed to add POINT...{e}")

    def deduct_points(self, authur, reaction_points):
        if self.conn:
            try:
                cursor = self.conn.cursor()

                cursor.execute("""
                UPDATE POINTS_WALLET
                SET points_balance = points_balance - ?
                WHERE authur = ?
                """, (reaction_points, authur))

                self.conn.commit()
            except Error as e:
                print(f"Failed to deduct POINTs...{e}")


# ________________________________-------

# create POINTS table

    def coins_wallet_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS COINS_WALLET (
                        id INTEGER PRIMARY KEY,
                        authur TEXT,
                        coins_balance INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print("Error creating coins wallet table...")

    # update coins
    # pass the user id and coins balance + coins
    def add_coins(self, authur, coins):
        if self.conn:
            try:
                cursor = self.conn.cursor()

                cursor.execute("""
                INSERT INTO COINS_WALLET (authur, coins_balance)
                VALUES (?, 0)
                """, (authur,))

                cursor.execute("""
                UPDATE COINS_WALLET
                SET coins_balance = coins_balance + ?
                WHERE authur = ?
                """, (coins, authur))
                self.conn.commit()
            except Error as e:
                print(f"Failed to add coin...{e}")

    # get coins

    def get_coins(self, authur):
        try:
            cursor = self.conn.cursor()

            cursor.execute("""
            SELECT coins_balance FROM COINS_WALLET
            WHERE authur = ?
            """, (authur,))

            row = cursor.fetchone()

            return row["coins_balance"] if row else 0
        except Error as e:
            print(f"Failed to add coin(s)...{e}")

    # update coins
    # pass the user id and points balance - reaction points
    def deduct_coins(self, authur, coins):
        if self.conn:
            try:
                cursor = self.conn.cursor()

                cursor.execute("""
                UPDATE COINS_WALLET
                SET coins_balance = coins_balance - ?
                WHERE authur = ?
                """, (coins, authur))

                self.conn.commit()
            except Error as e:
                print(f"Failed to deduct coins...{e}")


####################################### POINTS TRANSACTION HISTORY#######################################
# create POINTS table

    def points_transactions_table(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS POINTS_TRANSACTIONS (
                        id INTEGER PRIMARY KEY,
                        authur INTEGER,
                        type TEXT,
                        amount TEXT, 
                        post_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                self.conn.commit()
            except Error as e:
                print("Error creating SESSIONS table...")

    # add new points to database
    def add_points_transaction(self, authur, type, amount, post_id):
        if self.conn:
            try:
                sql = "INSERT INTO POINTS_TRANSACTIONS (authur, type, amount, post_id) VALUES (?,?,?,?)"
                cursor = self.conn.cursor()
                cursor.execute(sql, (authur, type, amount, post_id))
                self.conn.commit()
            except Error as e:
                print(f"Failed to add POINT...{e}")


# -------------------------------------------------------------close the database connection---------------------------------------------

    # close connection to database


    def close_connection(self):
        if self.conn:
            self.conn.close()
            self.conn = None
