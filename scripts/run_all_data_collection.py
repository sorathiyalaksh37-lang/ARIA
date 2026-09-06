#!/usr/bin/env python3
"""
ARIA Master Data Collection Script
==================================
Runs all data collection scripts in sequence.

Author: ARIA Data Engineering Team
Date: 2026-08-22
Version: 1.0
"""

import logging
import os
import subprocess
import sys
import time
from datetime import datetime

# Setup logging
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, "master_data_collection.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SCRIPTS = [
    ("hospital_scraper.py", "Hospital Data Collection"),
    ("ambulance_scraper.py", "Ambulance Data Collection"),
    ("blood_bank_scraper.py", "Blood Bank Data Collection"),
    ("incident_generator.py", "Incident Data Generation"),
]

def run_script(script_name: str, description: str) -> bool:
    """Run a data collection script."""
    logger.info("=" * 70)
    logger.info(f"Starting: {description}")
    logger.info("=" * 70)
    
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    try:
        start_time = time.time()
        
        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            logger.info(f"✓ {description} completed successfully in {elapsed_time:.2f} seconds")
            return True
        else:
            logger.error(f"✗ {description} failed with return code {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"✗ {description} timed out after 1 hour")
        return False
    except Exception as e:
        logger.error(f"✗ {description} failed with exception: {e}")
        return False

def main():
    """Run all data collection scripts."""
    overall_start = time.time()
    
    logger.info("\n" + "=" * 70)
    logger.info("ARIA MASTER DATA COLLECTION STARTED")
    logger.info("=" * 70)
    logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Scripts to run: {len(SCRIPTS)}")
    logger.info("=" * 70 + "\n")
    
    results = {}
    
    for script_name, description in SCRIPTS:
        success = run_script(script_name, description)
        results[description] = success
        
        # Add delay between scripts
        if script_name != SCRIPTS[-1][0]:
            logger.info("Waiting 5 seconds before next script...\n")
            time.sleep(5)
    
    overall_elapsed = time.time() - overall_start
    
    # Print summary
    logger.info("\n" + "=" * 70)
    logger.info("DATA COLLECTION SUMMARY")
    logger.info("=" * 70)
    
    success_count = sum(1 for v in results.values() if v)
    
    for description, success in results.items():
        status = "✓ SUCCESS" if success else "✗ FAILED"
        logger.info(f"{description:40s}: {status}")
    
    logger.info("=" * 70)
    logger.info(f"Completed: {success_count}/{len(SCRIPTS)} scripts successful")
    logger.info(f"Total Time: {overall_elapsed:.2f} seconds ({overall_elapsed/60:.1f} minutes)")
    logger.info(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 70)
    
    if success_count == len(SCRIPTS):
        logger.info("\n✓ ALL DATA COLLECTION COMPLETED SUCCESSFULLY!")
        logger.info("\nNext steps:")
        logger.info("1. Review data in data/raw/ directory")
        logger.info("2. Check summary reports in data/raw/*_summary.txt")
        logger.info("3. Proceed to data preprocessing")
        return 0
    else:
        logger.error("\n✗ SOME SCRIPTS FAILED. Please check logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
