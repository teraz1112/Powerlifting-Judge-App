from django.shortcuts import render
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import cv2
import mediapipe as mp
import time
import os

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose

def upload(request):
    if request.method == 'POST' and request.FILES['video']:
        video = request.FILES['video']
        fs = FileSystemStorage()
        filename = fs.save(video.name, video)
        video_path = os.path.join(settings.MEDIA_ROOT, filename)
        l_frame_url,r_frame_url = estimate_pose(video_path)
        return render(request, 'result.html', {'l_frame_url': l_frame_url, 'r_frame_url': r_frame_url})
    return render(request, 'upload.html')

def estimate_pose(video_path):
    # 動画の読み込み
    cap = cv2.VideoCapture(video_path)

    # Pose推定のためのモデルを読み込む
    with mp_pose.Pose(
        min_detection_confidence=0.1,
        min_tracking_confidence=0.7) as pose:
        while cap.isOpened():
            # 動画から1フレームを読み込む
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                break
            image.flags.writeable = False
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # 1フレームごとにPose推定を実行
            results = pose.process(image)
            # 腰の二点の座標を取得
            try:
                left_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP]
                right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
            except:
                pass

            # left_hipのy座標が最小値を取得
            try:
                if left_hip.y > l_min_y:
                    l_min_y = left_hip.y
                    l_min_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            except:
                l_min_y = 0
            
            # right_hipのy座標が最小値を取得
            try:
                if right_hip.y > r_min_y:
                    r_min_y = right_hip.y
                    r_min_img = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            except:
                r_min_y = 0

            # # 検出されたポーズの骨格をカメラ画像に重ねて描画
            # image.flags.writeable = True
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            # mp_drawing.draw_landmarks(
            #     image,
            #     results.pose_landmarks,
            #     mp_pose.POSE_CONNECTIONS,
            #     landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
            # # cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
            # if cv2.waitKey(5) & 0xFF == 27:
            #     break
    cap.release()
    timestamp = int(time.time())  # 現在のUNIXタイムスタンプを取得
    l_image_filename = f'l_min_{timestamp}.jpg'  # タイムスタンプを含むファイル名を作成
    r_image_filename = f'r_min_{timestamp}.jpg'  # タイムスタンプを含むファイル名を作成
    
    # 画像を保存
    l_image_path = os.path.join(settings.MEDIA_ROOT, l_image_filename)
    r_image_path = os.path.join(settings.MEDIA_ROOT, r_image_filename)
    cv2.imwrite(l_image_path, l_min_img)
    cv2.imwrite(r_image_path, r_min_img)
    
    # 保存した画像のURLを返す
    return os.path.join(settings.MEDIA_URL, l_image_filename), os.path.join(settings.MEDIA_URL, r_image_filename)



def result(request):
    # result.htmlでフレーム画像を表示
    return render(request, 'result.html')


