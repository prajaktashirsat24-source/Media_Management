from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    send_from_directory
)

import mysql.connector
import os


app = Flask(__name__)

app.secret_key = "media_management_secret_key"


# ============================================================
# Upload Configuration
# ============================================================

UPLOAD_FOLDER = "uploads"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {
    "png",
    "jpg",
    "jpeg",
    "gif"
}


def allowed_file(filename):

    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# MySQL Database Connection
# ============================================================

def get_db_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MediaAdmin@2026",
        database="media_management"
    )


# ============================================================
# Home
# ============================================================

@app.route("/")
def home():

    return redirect(url_for("login"))


# ============================================================
# Admin Login
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin123":

            session["admin_logged_in"] = True

            return redirect(url_for("dashboard"))

        return "Invalid Username or Password"

    return render_template("login.html")


# ============================================================
# Admin Dashboard
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    return render_template("dashboard.html")


# ============================================================
# PRESS RELEASES
# ============================================================

# Add Press Release
@app.route("/add-press-release", methods=["GET", "POST"])
def add_press_release():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        release_date = request.form["release_date"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO press_releases
            (title, description, release_date)
            VALUES (%s, %s, %s)
            """,
            (
                title,
                description,
                release_date
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("press_releases"))

    return render_template("add_press_release.html")


# Press Release List
@app.route("/press-releases")
def press_releases():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, description, release_date
        FROM press_releases
        ORDER BY release_date DESC
        """
    )

    releases = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "press_releases.html",
        releases=releases
    )


# Edit Press Release
@app.route(
    "/edit-press-release/<int:release_id>",
    methods=["GET", "POST"]
)
def edit_press_release(release_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        title = request.form["title"]
        description = request.form["description"]
        release_date = request.form["release_date"]

        cursor.execute(
            """
            UPDATE press_releases
            SET title = %s,
                description = %s,
                release_date = %s
            WHERE id = %s
            """,
            (
                title,
                description,
                release_date,
                release_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("press_releases"))

    cursor.execute(
        """
        SELECT id, title, description, release_date
        FROM press_releases
        WHERE id = %s
        """,
        (release_id,)
    )

    release = cursor.fetchone()

    cursor.close()
    connection.close()

    if not release:

        return "Press Release not found"

    return render_template(
        "edit_press_release.html",
        release=release
    )


# Delete Press Release
@app.route("/delete-press-release/<int:release_id>")
def delete_press_release(release_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM press_releases
        WHERE id = %s
        """,
        (release_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("press_releases"))


# ============================================================
# MEDIA COVERAGE
# ============================================================

# Add Media Coverage
@app.route("/add-media-coverage", methods=["GET", "POST"])
def add_media_coverage():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    if request.method == "POST":

        title = request.form["title"]
        url = request.form["url"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO media_coverage
            (title, url)
            VALUES (%s, %s)
            """,
            (
                title,
                url
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("media_coverage"))

    return render_template("add_media_coverage.html")


# Media Coverage List
@app.route("/media-coverage")
def media_coverage():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, title, url
        FROM media_coverage
        ORDER BY created_at DESC
        """
    )

    coverages = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "media_coverage.html",
        coverages=coverages
    )


# Edit Media Coverage
@app.route(
    "/edit-media-coverage/<int:coverage_id>",
    methods=["GET", "POST"]
)
def edit_media_coverage(coverage_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == "POST":

        title = request.form["title"]
        url = request.form["url"]

        cursor.execute(
            """
            UPDATE media_coverage
            SET title = %s,
                url = %s
            WHERE id = %s
            """,
            (
                title,
                url,
                coverage_id
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("media_coverage"))

    cursor.execute(
        """
        SELECT id, title, url
        FROM media_coverage
        WHERE id = %s
        """,
        (coverage_id,)
    )

    coverage = cursor.fetchone()

    cursor.close()
    connection.close()

    if not coverage:

        return "Media Coverage not found"

    return render_template(
        "edit_media_coverage.html",
        coverage=coverage
    )


# Delete Media Coverage
@app.route("/delete-media-coverage/<int:coverage_id>")
def delete_media_coverage(coverage_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM media_coverage
        WHERE id = %s
        """,
        (coverage_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("media_coverage"))


# ============================================================
# IMAGE GALLERY
# ============================================================

# Add Image
@app.route("/add-image", methods=["GET", "POST"])
def add_image():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    if request.method == "POST":

        image = request.files["image"]
        description = request.form["description"]

        if image and allowed_file(image.filename):

            filename = image.filename

            image_path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            image.save(image_path)

            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute(
                """
                INSERT INTO image_gallery
                (image_path, description)
                VALUES (%s, %s)
                """,
                (
                    image_path,
                    description
                )
            )

            connection.commit()

            cursor.close()
            connection.close()

            return redirect(url_for("image_gallery"))

        return "Invalid Image File"

    return render_template("add_image.html")


# Serve Uploaded Images
@app.route("/uploads/<path:filename>")
def uploaded_file(filename):

    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename
    )


# Image Gallery List
@app.route("/image-gallery")
def image_gallery():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, image_path, description
        FROM image_gallery
        ORDER BY uploaded_at DESC
        """
    )

    images = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "image_gallery.html",
        images=images
    )


# Delete Image
@app.route("/delete-image/<int:image_id>")
def delete_image(image_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT image_path
        FROM image_gallery
        WHERE id = %s
        """,
        (image_id,)
    )

    image = cursor.fetchone()

    if image:

        image_path = image[0]

        if os.path.exists(image_path):

            os.remove(image_path)

        cursor.execute(
            """
            DELETE FROM image_gallery
            WHERE id = %s
            """,
            (image_id,)
        )

        connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("image_gallery"))


# ============================================================
# VIDEOS
# ============================================================

# Add Video
@app.route("/add-video", methods=["GET", "POST"])
def add_video():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    if request.method == "POST":

        video_url = request.form["video_url"]
        description = request.form["description"]

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO videos
            (video_url, description)
            VALUES (%s, %s)
            """,
            (
                video_url,
                description
            )
        )

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for("videos"))

    return render_template("add_video.html")


# Video List
@app.route("/videos")
def videos():

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id, video_url, description
        FROM videos
        ORDER BY uploaded_at DESC
        """
    )

    video_list = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        "videos.html",
        videos=video_list
    )


# Delete Video
@app.route("/delete-video/<int:video_id>")
def delete_video(video_id):

    if not session.get("admin_logged_in"):

        return redirect(url_for("login"))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM videos
        WHERE id = %s
        """,
        (video_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for("videos"))


# ============================================================
# PUBLIC MEDIA PAGE
# ============================================================

@app.route("/media")
def media_page():

    connection = get_db_connection()
    cursor = connection.cursor()

    # Press Releases
    cursor.execute(
        """
        SELECT id, title, description, release_date
        FROM press_releases
        ORDER BY release_date DESC
        """
    )

    releases = cursor.fetchall()


    # Media Coverage
    cursor.execute(
        """
        SELECT id, title, url
        FROM media_coverage
        ORDER BY created_at DESC
        """
    )

    coverages = cursor.fetchall()


    # Image Gallery
    cursor.execute(
        """
        SELECT id, image_path, description
        FROM image_gallery
        ORDER BY uploaded_at DESC
        """
    )

    images = cursor.fetchall()


    # Videos
    cursor.execute(
        """
        SELECT id, video_url, description
        FROM videos
        ORDER BY uploaded_at DESC
        """
    )

    videos = cursor.fetchall()


    cursor.close()
    connection.close()

    return render_template(
        "media_page.html",
        releases=releases,
        coverages=coverages,
        images=images,
        videos=videos
    )


# ============================================================
# ADMIN LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.pop("admin_logged_in", None)

    return redirect(url_for("login"))


# ============================================================
# Run Application
# ============================================================

if __name__ == "__main__":

    app.run(debug=True)