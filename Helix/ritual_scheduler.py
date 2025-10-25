import schedule
import time
import subprocess
from datetime import datetime
import os

def run_weekly_ritual():
    """Execute Neti-Neti burn ritual every Sunday 20:00 UTC"""
    print(f"[{datetime.utcnow()}] Initiating weekly Neti-Neti ritual...")
    print(f"DEBUG: Current working directory: {os.getcwd()}")
    
    # Define paths relative to the repository root
    ritual_engine_path = os.path.join(os.path.dirname(__file__), "z88_ritual_engine.py")
    shadow_log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Shadow", "archive")
    shadow_log_path = os.path.join(shadow_log_dir, "ritual_log.txt")
    print(f"DEBUG: ritual_engine_path: {ritual_engine_path}")
    print(f"DEBUG: shadow_log_dir: {shadow_log_dir}")
    print(f"DEBUG: shadow_log_path: {shadow_log_path}")
    
    os.makedirs(shadow_log_dir, exist_ok=True)

    # Run Z-88 ritual engine
    result = subprocess.run(
        ["python", ritual_engine_path, "--dream", "--steps=5"], # Reduced steps for quicker test
        capture_output=True,
        text=True
    )
    
    print(f"DEBUG: Subprocess stdout:\n{result.stdout}")
    print(f"DEBUG: Subprocess stderr:\n{result.stderr}")
    # Log results
    with open(shadow_log_path, "a") as f:
        f.write(f"\n=== Ritual {datetime.utcnow()} ===\n")
        f.write(result.stdout)
        f.write(result.stderr) # Also log stderr for debugging
    
    print("Ritual complete. Results logged.")

if __name__ == "__main__":
    run_weekly_ritual()

