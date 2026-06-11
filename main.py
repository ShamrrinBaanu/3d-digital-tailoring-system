import cv2
import numpy as np

# =====================================================================
# CONFIGURATION FOR A4 SHEET CALIBRATION
# =====================================================================
REAL_WIDTH_CM = 30.0       # A4 long edge in landscape mode
FIXED_DISTANCE_CM = 100.0  # Distance from camera to paper (1 meter)
# =====================================================================

points = []

def click_event(event, x, y, flags, params):
    """Callback function to record mouse clicks on the corners of the paper."""
    global points
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append((x, y))
        # Draw a small circle where the user clicked
        cv2.circle(img_copy, (x, y), 5, (0, 0, 255), -1)
        cv2.imshow("Calibrate Window", img_copy)
        
        if len(points) == 2:
            print("✅ Two points captured!")

def calibrate_focal_length():
    global img_copy, points
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Error: Cannot open webcam")
        return

    print("\n=== STEP 1: CAPTURE CALIBRATION IMAGE ===")
    print(f"1. Ensure your A4 paper is exactly {FIXED_DISTANCE_CM} cm away.")
    print("2. Press SPACEBAR to capture the frame.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Webcam Feed", frame)
        if cv2.waitKey(1) & 0xFF == 32: # Spacebar
            captured_frame = frame.copy()
            break
            
    cap.release()
    cv2.destroyAllWindows()

    # Step 2: Interactive Corner Selection
    img_copy = captured_frame.copy()
    cv2.namedWindow("Calibrate Window")
    cv2.setMouseCallback("Calibrate Window", click_event)

    print("\n=== STEP 2: SELECT THE WIDTH ===")
    print("1. Click exactly on the LEFT edge corner of the A4 paper.")
    print("2. Click exactly on the RIGHT edge corner of the A4 paper.")
    print("3. Press 'c' to calculate the focal length once both points are clicked.")

    while True:
        cv2.imshow("Calibrate Window", img_copy)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('c') and len(points) == 2:
            # Calculate pixel distance between the two clicked points
            p1 = np.array(points[0])
            p2 = np.array(points[1])
            pixel_width = np.linalg.norm(p1 - p2)
            
            # Pinhole Camera Formula: Focal Length = (Pixels * Distance) / Real Width
            focal_length_px = (pixel_width * FIXED_DISTANCE_CM) / REAL_WIDTH_CM
            
            print("\n" + "="*50)
            print(f"🎉 YOUR HP LAPTOP WEBCAM FOCAL LENGTH IS:")
            print(f"KNOWN_FOCAL_LENGTH_PX = {focal_length_px:.2f}")
            print("="*50)
            print("Copy this number and paste it into the measurement code below.")
            break
        elif key == 27: # ESC to exit
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrate_focal_length()