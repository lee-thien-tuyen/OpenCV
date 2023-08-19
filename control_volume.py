import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#khoi tao cac cong cu de ve cac diem anh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
#volume.GetMute()
#volume.GetMasterVolumeLevel() #
volRange=volume.GetVolumeRange()  #phạm vi âm lương -65 -> 0
print(volume.GetVolumeRange())

print(volRange[0])
print(volRange[1])
minVol = volRange[0]
maxVol = volRange[1]


cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")

      continue
    lmList = []
    handNo = 0

    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)


    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    if results.multi_hand_landmarks:
      for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(
            image,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
      myHand = results.multi_hand_landmarks[handNo]
      for id, lm in enumerate(myHand.landmark):
          # print(id, lm)
          h, w, c = image.shape
          cx, cy = int(lm.x * w), int(lm.y * h)
          # print(id, cx, cy)
          lmList.append([id, cx, cy])

    if len(lmList)!= 0:
        # cần sử dụng 2 ngón trỏ và ngón cái (point 4, và 8)
        #print(lmList[4],lmList[8]) # đẩy về giá trị điểm 4 và 8
        x1, y1= lmList[4][1], lmList[4][2] # get tọa độ đầu ngón cái
        x2, y2 = lmList[8][1], lmList[8][2] # get tọa độ đầu ngón trỏ


        # vẽ 2 đường tròn trên 2 đầu ngón cái và ngón trỏ
        cv2.circle(image, (x1, y1), 8, (255, 0, 255), -1)
        cv2.circle(image, (x2, y2), 8, (255, 0, 255), -1)
        cv2.line(image,(x1,y1),(x2,y2),(255,0,255),3)
        # vẽ đường tròn giữa 2 đường thằng nối ngón cái và ngón giữa
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        cv2.circle(image, (cx, cy), 8, (255, 0, 255), -1)

        #xác định độ dài đoạn thẳng nối từ ngón trái đến ngón trỏ
        length= math.hypot(x2-x1,y2-y1)
        print("length: ",length)
        """
            độ dài tay tôi vào khoảng 18 đến 205 và cũng tùy vào việc bạn đữa gần cam hay không
            dải âm lượng từ -65 đến 0 """

        # scale độ dài tay và dải âm lượng
        vol = np.interp(length,[18,205],[minVol,maxVol])
        # điều chỉnh âm lượng
        volume.SetMasterVolumeLevel(vol, None)
        # scale đồ dài tay và % hiệnr thị
        volBar = np.interp(length, [18, 205], [400, 150])
        vol_tyle = np.interp(length, [18, 205], [0, 100])

        if length<18 :
            cv2.circle(image, (cx, cy), 15, (0, 255, 0), -1) # vẽ 1 đường tròn khác màu để báo giá trị min

        cv2.rectangle(image,(50,150),(100,400),(0,255,0),3)
        cv2.rectangle(image,(50,int(volBar)),(100,400),(0,255,0),-1)
        # show %vol lên màn hình
        cv2.putText(image, f"{int(vol_tyle)} %", (50, 130), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0), 3)


    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) == ord('q'):
      break
cap.release()
cv2.destroyAllWindows()