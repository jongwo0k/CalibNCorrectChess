import numpy as np
import cv2 as cv

"""
camera calibration 결과 불러오기
K= np.array([[1693.50596237, 0, 963.46640565],
            [0, 1694.80955986, 541.05422696],
            [0, 0, 1]])
dist_coeff = np.array([0.00279195, -0.40559272, 0.00018096, 0.000266, 1.53740798])
"""

# npz에서 불러오기
data = np.load(r"C:\CV\calibration_result.npz") # npz 파일 경로
K = data["K"]
dist_coeff = data["dist"]

# video 불러오기
video_file = r"C:\CV\chessboard.mp4" # video 파일 경로
video = cv.VideoCapture(video_file)
assert video.isOpened(), 'Cannot read the given input, ' + video_file

# distortion correction
show_rectify = True
map1, map2 = None, None

while True:
    # Image 불러오기
    valid, img = video.read()
    if not valid:
        break

    # 왜곡 보정 (cv.undistort()가능)
    info = "Original"
    if show_rectify:
        if map1 is None or map2 is None:
            map1, map2 = cv.initUndistortRectifyMap(K, dist_coeff, None, None, (img.shape[1], img.shape[0]), cv.CV_32FC1)
        img = cv.remap(img, map1, map2, interpolation=cv.INTER_LINEAR)
        info = "Rectified"
    cv.putText(img, info, (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))

    # 키 설정
    cv.imshow("Geometric Distortion Correction", img)
    key = cv.waitKey(10)
    if key == ord(' '):     # Space : 정지
        key = cv.waitKey()
        
    if key == 27:           # ESC : 종료
        break
    
    elif key == ord('\t'):  # Tab : 모드 변경
        show_rectify = not show_rectify

# 종료 시 리소스 해제
video.release()
cv.destroyAllWindows()
