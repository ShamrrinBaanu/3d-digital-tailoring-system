from ultralytics import YOLO
import cv2
import numpy as np
import time


# Load your YOLO11 Pose model
model = YOLO("yolo11n-pose.pt")

# YOUR EXACT CALIBRATION VALUE:
KNOWN_FOCAL_LENGTH_PX = 550.01  

# The exact distance (in cm) the person must stand from your laptop camera
PERSON_DISTANCE_CM = 250.0  # 2.5 Meters

# --- ANATOMICAL EXTERNAL PADDING CONSTANTS---
SHOULDER_PADDING_CM = 2.0   
WAIST_PADDING_CM = 1.5

def measure_full_body_with_timer():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Laptop webcam is unavailable.")
        return

    print("\n=== COMPLETE FULL-BODY MEASUREMENT MODE (10s TIMER ACTIVE) ===")
    print(f"INSTRUCTION: Stand EXACTLY {PERSON_DISTANCE_CM / 100:.2f} meters away from the laptop camera.")
    print("Keep your laptop screen straight up (do not tilt it forward or backward).")
    print("Stand facing forward in an A-Pose (arms slightly out to your sides).")
    
    start_time = time.time()
    countdown_duration = 10  # 10 seconds countdown
    analysis_frame = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Calculate real-time countdown clock values
        elapsed_time = time.time() - start_time
        time_left = int(countdown_duration - elapsed_time)
        
        # Run YOLO inference live so the panel can see tracking feedback instantly
        results = model(frame, conf=0.4, verbose=False)
        display_frame = frame.copy()
        
        # Plot skeleton markers live on the screen during countdown
        for result in results:
            display_frame = result.plot()
            
        # Draw the big red timer and guidance on the live webcam stream view
        if time_left > 0:
            cv2.putText(display_frame, f"CAPTURING FRONT: {time_left}s", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            cv2.putText(display_frame, "Position yourself in an A-Pose facing forward!", (30, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            # Freeze the camera snapshot when the timer hits zero
            analysis_frame = frame.copy()
            break
            
        cv2.imshow("Live Measurement View", display_frame)
        
        # Emergency escape switch
        if cv2.waitKey(1) & 0xFF == 27: # ESC key
            cap.release()
            cv2.destroyAllWindows()
            print("Measurement canceled.")
            return

    cap.release()
    cv2.destroyAllWindows()

    print("\n📸 SNAP! Front picture locked. Processing full-body width and lengths...")
    results = model(analysis_frame, conf=0.5)
    annotated = analysis_frame.copy()

    for result in results:
        # Draw the standard YOLO skeleton points on final screen artifact
        annotated = result.plot()

        if result.keypoints is not None and len(result.keypoints.xy) > 0:
            kp = result.keypoints.xy[0].cpu().numpy()
            
            # Map structural body keypoints (COCO indexes)
            l_shoulder, r_shoulder = kp[5], kp[6]
            l_elbow, r_elbow       = kp[7], kp[8]
            l_wrist, r_wrist       = kp[9], kp[10]
            l_hip, r_hip           = kp[11], kp[12]
            l_knee, r_knee         = kp[13], kp[14]
            l_ankle, r_ankle       = kp[15], kp[16]

            # Core conversion math: Converts pixel length to real cm
            def get_real_distance(pt1, pt2):
                if pt1.any() and pt2.any() and not (np.all(pt1 == 0) or np.all(pt2 == 0)):
                    pixel_dist = np.linalg.norm(pt1 - pt2)
                    return (pixel_dist * PERSON_DISTANCE_CM) / KNOWN_FOCAL_LENGTH_PX
                return 0.0

            # 1. WIDTH CALCULATIONS (With Outer Tissue Padding)
            joint_shoulder_dist = get_real_distance(l_shoulder, r_shoulder)
            total_shoulder_width = joint_shoulder_dist + SHOULDER_PADDING_CM if joint_shoulder_dist > 0 else 0.0

            joint_hip_dist = get_real_distance(l_hip, r_hip)
            total_waist_width = joint_hip_dist + WAIST_PADDING_CM if joint_hip_dist > 0 else 0.0

            # 2. LENGTH CALCULATIONS (Segment by Segment tracking)
            left_arm = get_real_distance(l_shoulder, l_elbow) + get_real_distance(l_elbow, l_wrist)
            right_arm = get_real_distance(r_shoulder, r_elbow) + get_real_distance(r_elbow, r_wrist)
            
            left_leg = get_real_distance(l_hip, l_knee) + get_real_distance(l_knee, l_ankle)
            right_leg = get_real_distance(r_hip, r_knee) + get_real_distance(r_knee, r_ankle)

            # Print data cleanly to your terminal output window
            print("\n" + "="*40)
            print("REAL-WORLD CALCULATED BODY METRICS:")
            print(f"Whole Shoulder Width : {total_shoulder_width:.2f} cm")
            print(f"Whole Waist Width    : {total_waist_width:.2f} cm")
            print(f"Left Arm Length      : {left_arm:.2f} cm")
            print(f"Right Arm Length     : {right_arm:.2f} cm")
            print(f"Left Leg Length      : {left_leg:.2f} cm")
            print(f"Right Leg Length     : {right_leg:.2f} cm")
            print("="*40)

            # Draw value text overlays directly onto the visual screen image
            font = cv2.FONT_HERSHEY_SIMPLEX
            
            display_metrics = [
                (f"Shoulders: {total_shoulder_width:.1f} cm", l_shoulder, (0, 255, 0)),
                (f"Waist: {total_waist_width:.1f} cm", l_hip, (255, 0, 0)),
                (f"L Arm: {left_arm:.1f} cm", l_elbow, (0, 255, 255)),
                (f"R Arm: {right_arm:.1f} cm", r_elbow, (0, 255, 255)),
                (f"L Leg: {left_leg:.1f} cm", l_knee, (0, 165, 255)),
                (f"R Leg: {right_leg:.1f} cm", r_knee, (0, 165, 255))
            ]
            
            for text, kp_pos, color in display_metrics:
                if kp_pos.any():
                    cv2.putText(annotated, text, (int(kp_pos[0]), int(kp_pos[1] - 15)), font, 0.5, color, 2)

    # Save output frame onto disk
    cv2.imwrite("full_body_output.png", annotated)
    print("\nResult image saved successfully as 'full_body_output.png'.")
    
    # Display the static output image on screen
    cv2.imshow("Final Full-Body Metrics", annotated)
    cv2.waitKey(7000) # Automatically closes after 7 seconds to prevent terminal freeze
    cv2.destroyAllWindows()

if __name__ == "__main__":
    measure_full_body_with_timer()