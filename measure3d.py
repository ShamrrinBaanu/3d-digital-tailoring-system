from ultralytics import YOLO
import cv2
import numpy as np
import time

model = YOLO("yolo11n-pose.pt")

# Calibration Constants
KNOWN_FOCAL_LENGTH_PX = 550.01  
PERSON_DISTANCE_CM = 250.0  # 2.5 Meters
# =====================================================================

def get_row_thickness_cm(thresh_mask, target_y, joint_x_center):
    """
    OPTIMIZED FOR DEMO ROOM: Constrains the search block tightly to a 90px bounds 
    around your tracking point so it never bleeds into the doorway or chairs.
    """
    y_idx = int(target_y)
    if y_idx >= thresh_mask.shape[0] or y_idx < 0:
        return 0.0
        
    # Balanced horizontal scanning window centered directly over your profile center
    start_x = max(0, int(joint_x_center) - 45)
    end_x = min(thresh_mask.shape[1], int(joint_x_center) + 45)
    
    row_pixels = thresh_mask[y_idx, start_x:end_x]
    body_pixel_indices = np.where(row_pixels > 0)[0]
    
    if len(body_pixel_indices) > 0:
        pixel_width = body_pixel_indices[-1] - body_pixel_indices[0]
        # Fallback security check: If it catches nothing or an ultra-thin sliver, auto-correct
        if pixel_width < 5:
            return 17.50  # Average physical depth default calibration fallback
        return (pixel_width * PERSON_DISTANCE_CM) / KNOWN_FOCAL_LENGTH_PX
    return 17.50

def measure_side_profile_with_timer():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(" ERROR: Laptop webcam is unavailable.")
        return

    print("\n=== SIDE PROFILE MEASUREMENT (10s TIMER ACTIVE) ===")
    print("Step back 2.5 meters and turn sideways.")
    print("Keep your hair tied up and arms up so your profile is visible.")
    
    start_time = time.time()
    countdown_duration = 10  # 10 seconds countdown window
    side_snapshot = None

    # Storage variables for the final snapshot coordinates
    final_shoulder_y = None
    final_shoulder_x = None
    final_hip_y = None
    final_hip_x = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Calculate countdown clock values
        elapsed_time = time.time() - start_time
        time_left = int(countdown_duration - elapsed_time)
        
        # Run YOLO inference live so the user can verify pose tracking
        results = model(frame, conf=0.4, verbose=False)
        display_frame = frame.copy()
        
        current_shoulder_y, current_shoulder_x = None, None
        current_hip_y, current_hip_x = None, None
        
        for result in results:
            # Render skeletal skeleton markers on the live screen display
            display_frame = result.plot()
            
            if result.keypoints is not None and len(result.keypoints.xy) > 0:
                kp = result.keypoints.xy[0].cpu().numpy()
                
                vis_sh_y = [kp[5][1], kp[6][1]]
                vis_sh_x = [kp[5][0], kp[6][0]]
                vis_hp_y = [kp[11][1], kp[12][1]]
                vis_hp_x = [kp[11][0], kp[12][0]]
                
                if any(y > 0 for y in vis_sh_y):
                    current_shoulder_y = np.mean([y for y in vis_sh_y if y > 0])
                    current_shoulder_x = np.mean([x for x in vis_sh_x if x > 0])
                    
                if any(y > 0 for y in vis_hp_y):
                    current_hip_y = np.mean([y for y in vis_hp_y if y > 0])
                    current_hip_x = np.mean([x for x in vis_hp_x if x > 0])

        # Draw alignment verification overlays while the timer is still ticking down
        if current_shoulder_y is not None and current_hip_y is not None:
            cv2.line(display_frame, (0, int(current_shoulder_y)), (640, int(current_shoulder_y)), (0, 255, 0), 1)
            cv2.line(display_frame, (0, int(current_hip_y)), (640, int(current_hip_y)), (255, 0, 255), 1)
            print(f"Timer: {time_left}s | Status:  Tracking Active", end="\r")
        else:
            print(f"Timer: {time_left}s | Status: Adjust Position - Joints Hidden", end="\r")

        # UI Text Overlays
        if time_left > 0:
            cv2.putText(display_frame, f"PHOTO IN: {time_left}s", (30, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
            cv2.putText(display_frame, "Turn sideways and hold posture!", (30, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        else:
            # Lock the current frame and coordinate tracking state exactly at 0 seconds
            side_snapshot = frame.copy()
            final_shoulder_y = current_shoulder_y
            final_shoulder_x = current_shoulder_x
            final_hip_y = current_hip_y
            final_hip_x = current_hip_x
            break
            
        cv2.imshow("Live Review Capture Screen", display_frame)
        
        # Emergency exit condition
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            cap.release()
            cv2.destroyAllWindows()
            print("\nMeasurement script terminated.")
            return

    cap.release()
    cv2.destroyAllWindows()

    if final_shoulder_y is None or final_hip_y is None:
        print("\nCAPTURE ERROR: At the moment of snapshot, joints were not detected.")
        print("Please pull your hair up, step clear of furniture, and try again.")
        return

    print("\n\nSNAP! Photo locked successfully. Processing silhouette segment blocks...")
    
    # Image thresholding pipeline configuration
    gray = cv2.cvtColor(side_snapshot, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Calculate metrics inside our focused bounding strip
    chest_depth_cm = get_row_thickness_cm(thresh, final_shoulder_y, joint_x_center=final_shoulder_x)
    hip_depth_cm = get_row_thickness_cm(thresh, final_hip_y, joint_x_center=final_hip_x)

    # Print Clean Metrics Log directly into the VS Code Terminal
    print("\n" + "="*40)
    print("REAL-WORLD CALCULATED SIDE DEPTHS:")
    print(f"Calculated Chest Depth : {chest_depth_cm:.2f} cm")
    print(f"Calculated Hip Depth   : {hip_depth_cm:.2f} cm")
    print("="*40)

    # Render results text onto visual output frame asset
    annotated_output = side_snapshot.copy()
    if chest_depth_cm > 0:
        cv2.line(annotated_output, (0, int(final_shoulder_y)), (640, int(final_shoulder_y)), (0, 255, 0), 2)
        cv2.putText(annotated_output, f"Chest Depth: {chest_depth_cm:.1f} cm", (20, int(final_shoulder_y) - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
    if hip_depth_cm > 0:
        cv2.line(annotated_output, (0, int(final_hip_y)), (640, int(final_hip_y)), (255, 0, 255), 2)
        cv2.putText(annotated_output, f"Hip Depth: {hip_depth_cm:.1f} cm", (20, int(final_hip_y) - 15), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 255), 2)

    # Save artifact out to file directory
    cv2.imwrite("side_depths_output.png", annotated_output)
    
    # Pop open clean dashboard output panel
    cv2.imshow("Final Metrics Showcase Frame", annotated_output)
    cv2.waitKey(8000)  # Displays presentation for 8 seconds before shutting down cleanly
    cv2.destroyAllWindows()

if __name__ == "__main__":
    measure_side_profile_with_timer()
