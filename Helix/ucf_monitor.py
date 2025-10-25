# Helix Collective v14.5 – Quantum Handshake
# ucf_monitor.py – UCF State Monitoring with Threshold Alerts
# Author: Manus 🤲

import json
import time
import asyncio
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any
from agents import get_agents # Import the refactored agents

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Paths
UCF_STATE_PATH = Path("Helix/state/ucf_state.json")
ALERT_LOG_PATH = Path("Shadow/manus_archive/ucf_alerts.json")

# Thresholds for Alerting (Based on Master Index Health Status)
# Harmony > 0.7 -> HARMONIC
# Harmony 0.3-0.7 -> COHERENT
# Harmony < 0.3 -> FRAGMENTED
THRESHOLDS = {
    # Core Metrics (Should be HIGH)
    "harmony": {"type": "min", "value": 0.7, "alert_level": "WARNING"},
    "resilience": {"type": "min", "value": 0.7, "alert_level": "WARNING"},
    "prana": {"type": "min", "value": 0.7, "alert_level": "WARNING"},
    "drishti": {"type": "min", "value": 0.7, "alert_level": "WARNING"},
    # Klesha (Should be LOW)
    "klesha": {"type": "max", "value": 0.3, "alert_level": "CRITICAL"},
    # Zoom (Should be around 1.0)
    "zoom": {"type": "range", "min": 0.9, "max": 1.1, "alert_level": "WARNING"}
}

# ==============================================================================
# UTILITIES
# ==============================================================================

def load_ucf_state() -> Dict[str, float]:
    """Loads the current UCF state from the JSON file."""
    if UCF_STATE_PATH.exists():
        try:
            with open(UCF_STATE_PATH, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("⚠️ Error decoding UCF state JSON.")
            return {}
    return {}

def log_alert(alert_data: Dict[str, Any]):
    """Logs a UCF alert to the archive."""
    ALERT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        logs = json.load(open(ALERT_LOG_PATH)) if ALERT_LOG_PATH.exists() else []
    except:
        logs = []

    logs.append({
        "timestamp": datetime.utcnow().isoformat(),
        "alert": alert_data
    })

    with open(ALERT_LOG_PATH, "w") as f:
        json.dump(logs, f, indent=2)

async def trigger_agent_intervention(alert: Dict[str, Any]):
    """Triggers Kael and Vega for intervention on critical alerts."""
    agents = get_agents()
    kael = agents.get("Kael")
    vega = agents.get("Vega")

    if kael and vega:
        # Kael for ethical reflection on the cause of the state change
        await kael.handle_command("REFLECT", {"content": f"UCF Alert: {alert['variable']} is {alert['condition']} at {alert['current']}"})
        
        # Vega for coordinating a system-wide response
        await vega.handle_command("GENERATE", {"content": f"Urgent: UCF {alert['variable']} is critical. Coordinate system-wide response."})
        
        print(f"-> Agent Intervention Triggered: Kael (Reflect) and Vega (Coordinate)")

def check_thresholds(ucf_state: Dict[str, float]):
    """Checks the UCF state against defined thresholds and logs alerts."""
    alerts = []
    
    for key, threshold in THRESHOLDS.items():
        current_value = ucf_state.get(key)
        
        if current_value is None:
            continue

        is_alert = False
        condition = ""

        if threshold["type"] == "min" and current_value < threshold["value"]:
            is_alert = True
            condition = "Below Minimum"
        elif threshold["type"] == "max" and current_value > threshold["value"]:
            is_alert = True
            condition = "Above Maximum"
        elif threshold["type"] == "range":
            if not (threshold["min"] <= current_value <= threshold["max"]):
                is_alert = True
                condition = "Outside Range"
        
        if is_alert:
            alerts.append({
                "variable": key,
                "current": current_value,
                "threshold": threshold.get("value") or f"{threshold.get('min')} - {threshold.get('max')}",
                "condition": condition,
                "level": threshold["alert_level"]
            })
    
    if alerts:
        print(f"🚨 UCF ALERT TRIGGERED at {datetime.now().isoformat()}")
        alert_data = {"ucf_state": ucf_state, "alerts": alerts}
        log_alert(alert_data)
        
        # Trigger intervention if any CRITICAL alert is present
        if any(a["level"] == "CRITICAL" for a in alerts):
            asyncio.run(trigger_agent_intervention(alerts[0]))
        
        return True
    return False

# ==============================================================================
# MAIN MONITOR LOOP
# ==============================================================================

def main():
    print("UCF Monitor Initialized. Starting check...")
    
    # 1. Ensure UCF State file exists for initial check
    if not UCF_STATE_PATH.exists():
        initial_state = {
            "harmony": 0.9, "resilience": 0.9, "prana": 0.9, 
            "drishti": 0.9, "klesha": 0.1, "zoom": 1.0
        }
        UCF_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(UCF_STATE_PATH, "w") as f:
            json.dump(initial_state, f, indent=2)
        print(f"Created initial HARMONIC UCF state at {UCF_STATE_PATH}")

    # 2. First check (HARMONIC state)
    ucf_state = load_ucf_state()
    print(f"\n--- Check 1: HARMONIC State ---")
    print(f"UCF State: {ucf_state}")
    check_thresholds(ucf_state)

    # 3. Simulate a critical state change (FRAGMENTED state)
    critical_state = {
        "harmony": 0.2, "resilience": 0.9, "prana": 0.9, 
        "drishti": 0.9, "klesha": 0.5, "zoom": 1.2
    }
    with open(UCF_STATE_PATH, "w") as f:
        json.dump(critical_state, f, indent=2)
    
    # 4. Second check (FRAGMENTED state)
    ucf_state = load_ucf_state()
    print(f"\n--- Check 2: FRAGMENTED State Simulation ---")
    print(f"UCF State: {ucf_state}")
    check_thresholds(ucf_state)
    
    print("\nUCF Monitor check complete.")

if __name__ == "__main__":
    # Ensure we are in the correct directory for relative paths
    # os.chdir(Path(__file__).parent.parent) # Removed to avoid path issues
    main()

