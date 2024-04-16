import os
import cv2
import random
from flask import Flask, render_template, request
from gradio_client import Client


app = Flask(__name__)

def extract_random_frame(video_path, output_dir):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    random_frame_number = random.randint(0, total_frames - 1)
    cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_number)
    ret, frame = cap.read()
    if ret:
        frame_path = os.path.join(output_dir, 'image', f'random_frame.jpg')
        os.makedirs(os.path.dirname(frame_path), exist_ok=True)
        cv2.imwrite(frame_path, frame)
        return frame_path
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'Файл не был отправлен'

        file = request.files['file']
        if file.filename == '':
            return 'Файл не выбран'

        uploads_dir = os.path.join(app.static_folder, 'uploads')  # Путь к папке uploads внутри static

        if not os.path.exists(uploads_dir):
            os.makedirs(uploads_dir)

        file_path = os.path.join(uploads_dir, file.filename)
        file.save(file_path)

        random_frame_path = extract_random_frame(file_path, app.static_folder)

        client = Client("https://tonyassi-image-story-teller.hf.space/--replicas/liw84/")
        result = client.predict("static/image/random_frame.jpg")
        api_name="/predict"

        return render_template('upload.html', video_file=file, result=result)
    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)