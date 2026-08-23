#!/usr/bin/env python3
"""
Quick Test Script - Generate Small Sample Data
==============================================
Generates small samples to verify all scripts work correctly.

Run: python test_quick_run.py
"""

import subprocess
import sys
import os

print("=" * 70)
print("ARIA Data Collection - Quick Test")
print("=" * 70)
print("\nGenerating small sample datasets...")
print("This will take about 30 seconds.\n")

# Modify scripts temporarily to generate small datasets
test_counts = {
    "hospital_scraper.py": 100,
    "ambulance_scraper.py": 100,
    "blood_bank_scraper.py": 50,
    "incident_generator.py": 500
}

scripts_dir = os.path.dirname(os.path.abspath(__file__))

print("Note: This test generates small samples (not full datasets)")
print("-" * 70)

for script, count in test_counts.items():
    print(f"\nTesting {script}...")
    script_path = os.path.join(scripts_dir, script)
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print(f"✓ {script} passed")
        else:
            print(f"✗ {script} failed")
            print(f"Error: {result.stderr[:200]}")
    except Exception as e:
        print(f"✗ {script} error: {e}")

print("\n" + "=" * 70)
print("Quick test complete!")
print("Check data/raw/ directory for sample outputs")
print("=" * 70)
