from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pymysql.cursors
from werkzeug.utils import secure_filename
import os
import model_transfer as tran
import tensorflow as tf
from strength import main as stren
import matplotlib.pyplot as plt

app = Flask(__name__, static_folder='static', template_folder='templates')
app.secret_key = 'user_email'

# database configure
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "Zcy032619",
    "db": "web_transfer",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}


@app.route("/")
def index():
    print("jump to first page")
    return render_template("first_page.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    print("jump to login page")
    if request.method == "POST":
        email = request.form["email"]
        session['email'] = email
        password = request.form["password"]
        try:
            have_email = email_check(email)
            good_password = password_check(email, password)
            if have_email and good_password:
                print("well email and password match")
                return redirect(url_for('main_page'))
            elif not have_email:
                print("invalid email")
                error_msg = "Invalid email"
                return render_template("login.html", error_msg=error_msg, error_msge=error_msg)
            else:
                print("wrong password")
                error_msg = "Wrong password"
                return render_template("login.html", error_msg=error_msg, error_msgp=error_msg)
        except Exception as e:
            print(str(e))
    return render_template("login.html")


# check if the email and password in database matches
def password_check(email, password):
    print("checking password")
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE PasswordHash=%s and Email=%s'
    cursor.execute(query, (password, email))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# check if the email exist in the database
def email_check(email):
    print("checking email")
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT * FROM users WHERE Email=%s'
    cursor.execute(query, (email,))
    print(email)
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    print(result)
    return result


# select password from database by email
def password_get(email):
    print("select password")
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT PasswordHash FROM users WHERE Email=%s'
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# select hometown from database by email
def hometown_check(email):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT hometown FROM users WHERE Email=%s'
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# select name form database by email
def name_check(email):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT name FROM users WHERE Email=%s'
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


@app.route("/create", methods=["GET", "POST"])
def create():
    print("jump to signup page")
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        hometown = request.form["hometown"]
        name = request.form["name"]
        try:
            existing_user = email_check(email)
            if existing_user:
                return render_template("create.html", error_msg="Email already registered!")
            connection = pymysql.connect(**db_config)
            cursor = connection.cursor()
            query = ('INSERT INTO users (Email, PasswordHash, hometown, name, RegistrationDate) VALUES (%s, %s, %s, '
                     '%s, %s)')
            cursor.execute(query, (email, password, hometown, name, datetime.now()))
            connection.commit()
            print("well submit account")
            cursor.close()
            connection.close()
            return redirect(url_for("index"))
        except Exception as e:
            return str(e)
    else:
        return render_template('create.html')


@app.route("/terms_of_use")
def terms_of_use():
    print("jump to term of use page")
    return render_template("terms_ofuse.html")


@app.route("/policy")
def policy():
    print("jump to policy page")
    return render_template("policy.html")


@app.route("/login/forget_id", methods=["GET", "POST"])
def forget_id():
    print("jump to forget_id page")
    if request.method == "POST":
        email = request.form["email"]
        session['email'] = email
        hometown = request.form["hometown"]
        name = request.form["name"]
        existing_email = email_check(email)
        right_hometown = hometown_check(email=email)
        right_name = name_check(email=email)
        if existing_email:
            print("email is valid")
            print("input: ", hometown, name)
            print("actual: ", right_hometown[0]['hometown'], right_name[0]['name'])
            h = right_hometown[0]['hometown']
            n = right_name[0]['name']
            if h == hometown and n == name:
                return redirect(url_for("reset", email=email))
            else:
                print("not right to hometown or name")
                if h == hometown:
                    error_msg1 = "Wrong name or hometown!"
                    return render_template("forget-id.html", error_msg=error_msg1, error_msgn=error_msg1,
                                           error_msgh=error_msg1)
                else:
                    error_msg1 = "Wrong name or hometown!"
                    return render_template("forget-id.html", error_msg=error_msg1, error_msgh=error_msg1,
                                           error_msgn=error_msg1)
        else:
            print("email is not valid")
            error_msg2 = "Email is not valid!"
            return render_template("forget-id.html", error_msg=error_msg2, error_msge=error_msg2)
    return render_template("forget-id.html")


@app.route("/login/forget_id/reset", methods=["GET", "POST"])
def reset():
    print("jump to reset page")
    if request.method == "POST":
        email = session['email']
        print("This Email: ", email)
        pa = request.form["pa"]
        password = request.form["password"]
        if pa == password:
            change_password(email=email, new_password=password)
            print("change password ok")
            return redirect(url_for("index"))
        else:
            error_msg = "Not same password!"
            return render_template("reset.html", error_msg=error_msg)
    return render_template("reset.html")


# change the password to database by email
def change_password(email, new_password):
    print("change password")
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'UPDATE users SET PasswordHash = %s WHERE Email = %s'
    cursor.execute(query, (new_password, email,))
    result = cursor.fetchall()
    password = password_get(email)
    print("old_password:", password[0]['PasswordHash'], "\0\0new_password:", new_password)
    connection.commit()
    cursor.close()
    connection.close()
    return result


@app.route("/login/main_page")
def main_page():
    print("jump to main page")
    return render_template("main_page.html")


# get the picture from database
def picture_get(email):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'SELECT ImagePath FROM images WHERE email=%s'
    cursor.execute(query, (email,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


# upload the picture path to database
def picture_upload(email, picture_path):
    connection = pymysql.connect(**db_config)
    cursor = connection.cursor()
    query = 'INSERT INTO images (email, ImagePath, UploadDate) VALUES (%s, %s, %s)'
    cursor.execute(query, (email, picture_path, datetime.utcnow()))
    connection.commit()
    cursor.close()
    connection.close()


# 设置允许上传的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_PDF = {'pdf'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def load_and_preprocess_image(image_path):
    # 读取图片文件
    img = tf.io.read_file(image_path)
    # 解码为 JPEG 图片
    img = tf.image.decode_jpeg(img, channels=3)
    # 调整图片大小为模型期望的尺寸
    img = tf.image.resize(img, [224, 224])  # 假设模型期望的输入尺寸为 224x224
    # 归一化到 [0,1] 范围
    img /= 255.0
    # 增加批处理维度
    img = tf.expand_dims(img, axis=0)
    return img


@app.route("/login/main_page/transfer", methods=["GET", "POST"])
def transfer():
    print("jump to transfer page")
    if request.method == "POST":
        # 检查是否有文件上传
        if 'styleImage' not in request.files or 'contentImage' not in request.files:
            return "No file part", 400
        print("Ok get the web picture")
        style_file = request.files['styleImage']
        content_file = request.files['contentImage']
        if style_file.filename == '' or content_file.filename == '':
            return "No selected file", 400

        UPLOAD_FOLDER = 'testPicture'  # 或者使用绝对路径
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

        style_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(style_file.filename))
        content_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(content_file.filename))
        style_file.save(style_path)
        content_file.save(content_path)
        print("OK save")
        email = session.get('email')
        print("email:", email)
        stylized_img, img_path = tran.main(content_path, style_path, userEmail=email,
                                           load_path="static/result_picture", output_image_size=518)
        print("OK transfer")

        if os.path.exists(img_path):
            img_paths = img_path.replace("static/", "", 1)
            img_paths = img_paths.replace("\\", "/")
            try:
                os.remove(style_path)
                os.remove(content_path)
            except PermissionError as e:
                print(f"Error deleting file: {e}")
            print("stylized_img_path: " + img_paths)
            print("image_path exist")
            # img_paths don't have static/ can use url directly
            picture_upload(email, img_paths)
            # 重定向到结果页面或返回结果
            return render_template('type_transfer.html', img_path=img_paths)
        else:
            print("no this path")
    return render_template('type_transfer.html')


@app.route("/login/main_page/strength", methods=['GET', 'POST'])
def strength():
    if request.method == 'POST':
        UPLOAD_FOLDER = 'strength/demo'  # 或者使用绝对路径
        app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
        if 'styleImage' not in request.files:
            print("Not get the web picture")
            return "No file part", 400
        print("Ok get the web picture")
        style_file = request.files['styleImage']
        if style_file.filename == '':
            return "No selected file", 400
        style_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(style_file.filename))
        style_file.save(style_path)
        email = session.get('email')
        strength_img, img_path = stren.main(load_image_path=style_path,
                                            save_path="static/result_picture", email=email)
        if os.path.exists(img_path):
            img_paths = img_path.replace("static/", "", 1)
            img_paths = img_paths.replace("\\", "/")
            try:
                os.remove(style_path)
            except PermissionError as e:
                print(f"Error deleting file: {e}")
            print("stylized_img_path: " + img_paths)
            print("image_path exist")
            # img_paths don't have static/ can use url directly
            picture_upload(email, img_paths)
            img_paths = img_paths.replace("../", "", 1)
            # 重定向到结果页面或返回结果
            print("message img_path: ", img_paths)
            return render_template('picture_strength.html', img_path=img_paths)
        else:
            print("no this path")
    return render_template("picture_strength.html")


@app.route("/login/main_page/goblur", methods=['GET', 'POST'])
def goblur():
    return render_template("picture_goBlur.html")

if __name__ == "__main__":
    app.run(debug=True)
