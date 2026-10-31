import cv2

cap = None   # shared camera object

def start_camera():
    global cap
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: could not open camera.")
    else:
        print("Camera started successfully.")

def read_frame():
    ret, frame = cap.read()
    if not ret:
        print("Error: could not read frame.")
        return None
    return frame

def release_camera():
    global cap
    if cap is not None:
        cap.release()
        cap = None
        print("Camera released.")

if __name__ == "__main__":
    start_camera()

    while True:
        frame = read_frame()
        if frame is None:
            break

        cv2.imshow("Camera Test", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    release_camera()
    cv2.destroyAllWindows()()
