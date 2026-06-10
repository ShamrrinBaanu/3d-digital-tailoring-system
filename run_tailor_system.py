import subprocess
import re
import math
import time
import sys

def run_script_and_get_metrics(script_name):
    """
    Runs your existing script and reads the text output 
    printed to the terminal using regular expressions.
    Added encoding='utf-8' to fix Windows charmap crash.
    """
    process = subprocess.Popen(
        ["python", script_name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        encoding='utf-8'  
    )

    chest_value = 0.0
    hip_value = 0.0

    try:
        # Read the terminal prints live as they happen
        for line in process.stdout:
            print(line, end="")  # Keeps showing the original terminal prints to the panel
            
            # Look for Chest numbers in the terminal logs
            if "Chest" in line or "Shoulder Width" in line:
                match = re.search(r"(\d+\.\d+)", line)
                if match:
                    chest_value = float(match.group(1))
                    
            # Look for Hip or Waist numbers in the terminal logs
            if "Hip" in line or "Waist Width" in line:
                match = re.search(r"(\d+\.\d+)", line)
                if match:
                    hip_value = float(match.group(1))
    except Exception as e:
        print(f"\n⚠️ Log parsing notice: {e}")

    process.wait()
    return chest_value, hip_value

def pipeline_countdown(seconds, message):
    """Prints a clear terminal-based countdown timer for the review panel."""
    print(f"\n⏱️ {message.upper()} ⏱️")
    for i in range(seconds, 0, -1):
        print(f"👉 Starting in: {i} seconds... Get into position!", end="\r")
        time.sleep(1)
    print("\n🚀 LAUNCHING CAMERA NOW!\n")

def calculate_ramanujan_perimeter(w, d):
    """Calculates the 3D circumference using the Ellipse math formula."""
    a = w / 2.0  # Semi-major axis
    b = d / 2.0  # Semi-minor axis
    if a == 0 or b == 0:
        return 0.0
    return math.pi * (3 * (a + b) - math.sqrt((3 * a + b) * (a + 3 * b)))

def main():
    print("==================================================")
    print("🚀 AUTOMATED PIPELINE FUSION (WITH TIMER MODES)")
    print("==================================================")

    # 1. Front View Pipeline Phase
    front_width_file = "measure1.py" 
    pipeline_countdown(10, f"Step 1: Front Profile View ({front_width_file})")
    
    f_chest, f_hip = run_script_and_get_metrics(front_width_file)
    
    if f_chest == 0 and f_hip == 0:
        print("\n❌ Error: Front view script did not output valid metrics. Stopping pipeline.")
        return

    print(f"\n✅ Front View Metrics Logged -> Width 1: {f_chest} cm | Width 2: {f_hip} cm")

    # 2. Side View Pipeline Phase
    side_depth_file = "measure3d.py"
    pipeline_countdown(10, f"Step 2: Side Profile View ({side_depth_file})")
    
    s_chest, s_hip = run_script_and_get_metrics(side_depth_file)

    if s_chest == 0 and s_hip == 0:
        print("\n❌ Error: Side view script did not output valid metrics. Stopping pipeline.")
        return

    print(f"\n✅ Side View Metrics Logged -> Depth 1: {s_chest} cm | Depth 2: {s_hip} cm")

    # 3. Geometric Ellipse Mathematical Calculations
    chest_circumference = calculate_ramanujan_perimeter(f_chest, s_chest)
    hip_circumference = calculate_ramanujan_perimeter(f_hip, s_hip)

    # =====================================================================
    # FINAL PRESENTATION DASHBOARD
    # =====================================================================
    print("\n" + "="*50)
    print("        FINAL 3D PREDICTED BODY METRICS ")
    print("="*50)
    print(f" CALCULATED CHEST CIRCUMFERENCE : {chest_circumference:.2f} cm")
    print(f" CALCULATED HIP CIRCUMFERENCE   : {hip_circumference:.2f} cm")
    print("="*50)
    print("Data streams unified successfully. Ready for your review demo!")

if __name__ == "__main__":
    main()