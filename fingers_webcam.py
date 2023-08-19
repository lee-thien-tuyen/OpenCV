import cv2
import mediapipe as mp
import time
import os
#khoi tao cac cong cu de ve cac diem anh
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands
pTime = 0

FolderPath="Fingers"
lst=os.listdir(FolderPath)
# khai báo list chứa các mảng giá trị của các hình ảnh/
lst_2=[]
for i in lst:
    image=cv2.imread(f"{FolderPath}/{i}")  # Fingers/1.jpg , Fingers/2.jpg ...
    lst_2.append(image)

fingerid= [4,8,12,16,20]

cap = cv2.VideoCapture(0)
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as hands:
  while cap.isOpened():
    success, image = cap.read()
    cTime = time.time()

    if not success:
      print("Ignoring empty camera frame.")

      continue

    lmList = []
    lmList2 = []
    handNo = 0
    # Để cải thiện hiệu suất, tùy chọn đánh dấu hình ảnh là không thể ghi để chuyển qua tham chiếu.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # cho phep ve cac chu thich tren hinh anh
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

    if len(lmList) !=0:
        fingers= []
        # viết cho ngón cái (ý tường là điểm 4 ở bên trái hay bên phải điểm 2 )
        if lmList[fingerid[0]][1] < lmList[fingerid[0] - 1][1]:
            fingers.append(1)
            #print(lmList[fingerid[0]][1])
            #print(lmList[fingerid[0] - 1][1])
        else:
            fingers.append(0)
        print(lmList)
        # viết cho 4 ngón dài
        for id in range(1,5):
            if lmList[fingerid[id]][2] < lmList[fingerid[id]-2][2]:
                fingers.append(1)
                print(lmList[fingerid[id]][2])
                print(lmList[fingerid[id]-2][2])
            else:
                fingers.append(0)

        print(fingers)
        songontay=fingers.count(1)
        print(songontay)
        """
            chú ý mỗi bức ảnh sẽ đẩy về giá trị của 1 mảng có chiều rông, cao khác nhau
            ví dụ ảnh 0.png : print(lst_2[0].shape) kết quả (126, 110, 3)
            frame[0:126,0:110] = lst_2[0]
            do các bức ảnh 0-5.png khác nhau các giá trị width, height nên phải get theo shape """
        h, w, c = lst_2[songontay - 1].shape
        # nếu số ngón tay =0 thì lst_2[-1] đẩy về phần tử cuối cùng của list là ảnh 5 ngon tay
        image[0:h, 0:w] = lst_2[songontay - 1]

        # vẽ thêm hình chữ nhật hiện số ngón tay
        cv2.rectangle(image, (0, h), (w, h+50), (180, 255, 0), -1)
        cv2.putText(image, str(songontay), (35, h+40), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 5)

    # tính fps Frames per second - đây là  chỉ số khung hình trên mỗi giây

    fps=1/(cTime-pTime)
    pTime=cTime
    # show fps lên màn hình
    cv2.putText(image, f"FPS: {int(fps)}",(150,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)

    # lật hình anhr theo chiều ngang cv2.flip(image, 1)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) == ord('q'):
      break
cap.release()
cv2.destroyAllWindows()