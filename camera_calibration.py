import numpy as np
import cv2 as cv

# 비디오에서 이미지 선택(캡쳐)
def select_img_from_video(video_file, board_pattern, select_all=False, wait_msec=10, wnd_name='Camera Calibration'):
    # 비디오 불러오기
    video = cv.VideoCapture(video_file)
    assert video.isOpened()

    # 이미지 선택
    img_select = []
    while True:
        valid, img = video.read()
        if not valid:
            break
        
        # 모두 선택
        if select_all:
            img_select.append(img)
            
        else: # key로 장면 선택
            display = img.copy()
            cv.putText(display, f'NSelect: {len(img_select)}', (10, 25), cv.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0))
            cv.imshow(wnd_name, display)
            
            # 키 설정
            key = cv.waitKey(wait_msec)
            complete, pts = False, None
            
            if key == ord(' '): # Space : chessboard 코너 찾기
                complete, pts = cv.findChessboardCorners(img, board_pattern)
                cv.drawChessboardCorners(display, board_pattern, pts, complete)
                cv.imshow(wnd_name, display)
                key = cv.waitKey()
                
            if key == ord('\r'): # Enter : 이미지 선택
                if complete:
                    img_select.append(img)
                    print('Selection Complete')
                else:
                    print('Selection Failed')
                    
            if key == 27: # ESC : 종료
                break

    cv.destroyAllWindows()
    return img_select

def calib_camera_from_chessboard(images, board_pattern, board_cellsize, K=None, dist_coeff=None, calib_flags=None):
    # 2D point 준비 (꼭짓점 찾기)
    img_points = []
    
    for img in images:
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        complete, pts = cv.findChessboardCorners(gray, board_pattern)
        
        if complete:
            img_points.append(pts)
            print('Corner Detection Complete')
        else:
            print('Corner Detection Failed')
            
    assert len(img_points) > 0

    # 3D point 준비 (z = 0)
    obj_pts = [[c, r, 0] for r in range(board_pattern[1]) for c in range(board_pattern[0])]
    obj_points = [np.array(obj_pts, dtype=np.float32) * board_cellsize] * len(img_points)

    # Camera Calibration
    return cv.calibrateCamera(obj_points, img_points, gray.shape[::-1], K, dist_coeff, flags=calib_flags)

if __name__ == '__main__':
    video_file = r"C:\CV\chessboard.mp4"
    board_pattern = (10, 7)
    board_cellsize = 0.025

    img_select = select_img_from_video(video_file, board_pattern)
    assert len(img_select) > 0, 'No Selected Image'
    rms, K, dist_coeff, rvecs, tvecs = calib_camera_from_chessboard(img_select, board_pattern, board_cellsize)

    # 결과 출력
    np.set_printoptions(suppress=True)
    print('##### Camera Calibration Results #####')
    print(f'* The number of selected images = {len(img_select)}')
    print(f'* RMS error = {rms}')
    print(f'* Camera matrix (K) = \n{K}')
    print(f'* Distortion coefficient (k1, k2, p1, p2, k3, ...) = {dist_coeff.flatten()}')
    
    # 결과 저장 (.npz)
    save_path = r"C:\CV\calibration_result.npz"
    np.savez("calibration_result.npz", rms = rms, K = K, dist = dist_coeff, rvecs = rvecs, tvecs = tvecs)
    print(f"Calibration result saved to {save_path}")