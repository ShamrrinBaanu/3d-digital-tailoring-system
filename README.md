3D Digital Tailoring System 

An AI-powered computer vision pipeline designed to calculate accurate 3D human body circumferences from 2D camera feeds. By tracking body landmarks via YOLO11 Pose Estimation, capturing multi-view dimensions, and applying advanced geometric algorithms, this system replaces manual measuring tapes with an automated digital fitting room.

---

#Project Architecture

The system splits the vision processing into modular tasks across four core files:
1. main.py: The calibration script used to determine the camera lens's unique focal length.
2. measure1.py: Handles the front perspective to map body widths and skeletal lengths.
3. measure3d.py: Processes the side perspective silhouette using adaptive thresholding to map body depths.
4. run_tailor_system: Fuses data streams from both scripts using regular expressions to parse terminal outputs and applies Ramanujan's First Approximation for Elliptical Perimeters to calculate final 3D circumferences.

---

#Camera Calibration Guide (How to Use This Project):
This computes your specific camera's pixel-to-centimeter projection constant.

System Setup Requirements:
1. The Reference Object: A standard sheet of A4 paper (used because it has an exact physical length of 30.0 cm along its long edge in landscape orientation).
2. Setup Location: Tape or fix the A4 paper completely flat against a wall.
3. Hardware Distance: Position your laptop or webcam exactly 100.0 cm (1 meter) away from the wall, facing the paper directly.

Calibration Steps:
1. Execute the calibration tool:
   ```bash
   python main.py
   ```
2. A webcam preview window will launch. Ensure the wall-mounted paper is clearly visible and press the SPACEBAR to freeze the snapshot.

3. On the frozen window, carefully click the leftmost corner edge of the A4 paper, and then click the rightmost corner edge.

4. Press the 'c' key to execute the calculation.

Your terminal console will output your custom value:
YOUR WEBCAM FOCAL LENGTH IS:
KNOWN_FOCAL_LENGTH_PX = certain value(ex:550.01)

Copy your unique number and verify that it is updated as the KNOWN_FOCAL_LENGTH_PX variable at the top of your measure1.py and measure3d.py files.

# User Guide & Scanning Process

Follow these quick setup rules to ensure accurate 3D measurements.

# 1. Scan Setup & Preparation
* Clothing: Wear tight, form-fitting  or leggings. Baggy clothes will break the silhouette tracker.
* Contrast: Stand against a plain wall that is a completely different color than your clothes.
* Distance: Place your webcam at chest height and stand exactly 2.5 meters (250 cm) away. 

---

# 2. The 2-Step Auto-Scan

To launch the automated countdown pipeline, run:
```bash
python run_tailor_system.py
```
Phase 1: Front View (10s Timer)
Action: Stand completely straight facing the camera in an A-Pose (arms slightly out to your sides).

AI Output: Automatically captures structural shoulder/waist widths and arm/leg segment lengths.

Phase 2: Side View (10s Timer)
Action: Turn exactly 90 degrees sideways. Keep your posture straight and arms relaxed slightly backward.

AI Output: Automatically extracts your side chest and hip depth silhouettes.

#3. Volumetric Results Dashboard
The system automatically passes the multi-perspective data stream into Ramanujan's Elliptical Perimeter formula to print your finalized 3D circumferences:

        FINAL 3D PREDICTED BODY METRICS 
 CALCULATED CHEST CIRCUMFERENCE : 94.25 cm
 CALCULATED HIP CIRCUMFERENCE   : 102.10 cm
