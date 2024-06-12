# main.py
from flask import Flask, render_template, Response, jsonify, request
from werkzeug.utils import secure_filename
from banknote import userCertify, userCertify_filesave, compareFeature
from Coin_Detection import Coin_Detection, Coin_Detection_save
import os
import cv2
import time
import shutil

app = Flask(__name__)

toggle = True
last_processed_image = []
processed_images = {}  # 이미지 처리 결과를 저장할 딕셔너리


# 카메라 연결
def gen():
    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    while True:
        _, frame = camera.read()
        cv2.imwrite("static/pic.jpg", frame)

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + open("static/pic.jpg", "rb").read()
            + b"\r\n"
        )

    camera.release()
    cv2.destroyAllWindows()


def coin_process_filesave(file_name, money_process_filename):
    img_frame = cv2.imread(file_name)
    return Coin_Detection_save(img_frame, money_process_filename)


def coin_process(file_name):
    img_frame = cv2.imread(file_name)
    return Coin_Detection(img_frame)


def bill_process_filesave(file_name, money_process_filename):
    # 기능구현 - 지폐 검출후 imwrite
    img_frame = cv2.imread(file_name)
    return userCertify_filesave(img_frame, money_process_filename)


def bill_process(file_name):
    # 기능구현 - 지폐 검출후 imwrite
    img_frame = cv2.imread(file_name)
    return userCertify(img_frame)


def money_process_filesave(file_name, money_process_filename):
    result_flag = False
    if coin_process_filesave(file_name, money_process_filename):
        result_flag = True
    if bill_process_filesave(file_name, money_process_filename):
        result_flag = True
    return result_flag


def money_process(file_name):
    result_flag = False
    if coin_process(file_name):
        result_flag = True
    if bill_process(file_name):
        result_flag = True
    return result_flag


@app.route("/")
def index():
    image_folder = "static/image"
    processed_images.clear()  # 이미지 처리 결과 초기화

    for filename in os.listdir(image_folder):
        image_path = os.path.join(image_folder, filename)
        result = money_process(image_path)
        processed_images[filename] = result  # 이미지 파일 이름과 결과를 딕셔너리에 저장

    # 검출됨
    left_images = [
        (filename, result) for filename, result in processed_images.items() if result
    ]
    # 검출안됨
    right_images = [
        (filename, result)
        for filename, result in processed_images.items()
        if not result
    ]

    return render_template(
        "index.html", left_images=left_images, right_images=right_images
    )


@app.route("/get_images")
def get_images():
    left_images = []
    right_images = []

    # 이미지 딕셔너리를 순회하면서 결과에 따라 분류
    for filename, result in processed_images.items():
        image_info = {"filename": filename, "url": "/static/image/" + filename}
        if result:
            left_images.append(image_info)
        else:
            right_images.append(image_info)

    return jsonify(left_images=left_images, right_images=right_images)


@app.route("/video_feed")
def video_feed():
    return Response(gen(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/take_picture")
def take_picture():
    global last_processed_image

    timestamp = int(time.time())
    filename = f"static/real_time/origin_pic_{timestamp}.jpg"
    money_process_filename = f"static/real_time/process_pic_{timestamp}.jpg"

    cv2.imwrite(filename, cv2.imread("static/pic.jpg"))
    # 이미지 파일 처리 결과를 딕셔너리에 저장
    result = money_process_filesave(filename, money_process_filename)
    # processed_images[filename] = result

    # Save the last processed image filename
    last_processed_image = [os.path.basename(money_process_filename), result]

    img_url = "/" + filename
    test_url = "/" + money_process_filename
    return jsonify({"img_url": img_url, "test_url": test_url})


@app.route("/save_image", methods=["POST"])
def save_image():
    global last_processed_image
    try:
        if last_processed_image:
            src = os.path.join("static/real_time", last_processed_image[0])
            dst = os.path.join("static/image", last_processed_image[0])
            shutil.move(src, dst)
            processed_images[last_processed_image[0]] = last_processed_image[1]
            last_processed_image = []
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "message": "No image to save."})
    except Exception as e:
        print(e)
        return jsonify({"success": False, "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True)
