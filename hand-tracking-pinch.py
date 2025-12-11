import cv2
import mediapipe as mp
import pyautogui
import math

def hand_mouse_control():
    #Start camera
    cam = cv2.VideoCapture(0)
    
    #Initialize Mediapipe and Tracking
    mp_hands = mp.solutions.hands.Hands(max_num_hands=1)
    mp_drawing = mp.solutions.drawing_utils
    
    #Get screen size
    screen_width, screen_height = pyautogui.size()
    
    clicking = False
    pinch_threshold = 0.05
    
    #New Lines for smoothening
    smoothening = 12
    prev_x, prev_y = 0, 0
    
    #Keep window on top
    cv2.namedWindow("Hand Gesture Mouse", cv2.WINDOW_NORMAL)
    cv2.setWindowProperty("Hand Gesture Mouse", cv2.WND_PROP_TOPMOST, 1)
    
    #Process video frames
    while cam.isOpened():
        sucess, frame = cam.read()
        if not sucess:
            continue
        
        #Flip and convert color, and send to mediapipe
        frame = cv2.flip(frame, 1)
        rbg_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_hands.process(rbg_frame)
        
        #Add hand landmarks
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp.solutions.hands.HAND_CONNECTIONS)
                
                #Get index finger tip position
                index_finger = hand_landmarks.landmark[8]
                x = int(index_finger.x * frame.shape[1])
                y = int(index_finger.y * frame.shape[0])
                
                screen_x = int(index_finger.x * screen_width)
                screen_y = int(index_finger.y * screen_height)
                # pyautogui.moveTo(screen_x, screen_y)
                # New Lines
                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening
                
                # Ignore tiny movements
                if abs(curr_x - prev_x) < 2 and abs(curr_y - prev_y) < 2:
                    continue

                pyautogui.moveTo(curr_x, curr_y)

                prev_x, prev_y = curr_x, curr_y
                
                #Decoration to fingertip
                cv2.circle(frame, (x, y), 10, (0, 255, 0), -1)
                
                #Pinch detection
                thumb_tip = hand_landmarks.landmark[4]
                dx = thumb_tip.x - index_finger.x
                dy = thumb_tip.y - index_finger.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance < pinch_threshold and not clicking:
                    pyautogui.click() 
                    clicking = True
                elif distance >= pinch_threshold and clicking:
                    clicking = False
                    
        cv2.imshow("Hand Gesture Mouse", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
    cam.release()
    cv2.destroyAllWindows()
                
if __name__ == "__main__":
    hand_mouse_control()