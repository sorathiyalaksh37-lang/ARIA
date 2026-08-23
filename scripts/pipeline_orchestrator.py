#!/usr/bin/env python3
"""
ARIA Pipeline Orchestrator
===========================
End-to-end orchestration of the complete Phase 1 data pipeline.

Author: ARIA Data Engineering Team
Date: August 2026
Version: 1.0

Pipeline Steps:
1. Create required directories
2. Run hospital scraper
3. Run ambulance scraper
4. Run blood bank scraper
5. Run incident generator
6. Run data preprocessor
7. Generate data quality report
8. Archive raw data
9. Prepare final datasets

Features:
- Progress tracking with tqdm
- Comprehensive logging
- Error handling with retries
- Checkpointing (resume from failure)
- Time tracking for each step
- Resource usage monitoring
- Output summary JSON
"""

import os
import sys
import json
import time
import logging
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import psutil

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False
    print("⚠️  tqdm not available. Progress bars disabled.")

# ============================================================================
# CONFIGURATION
# ============================================================================

BASE_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
ARCHIVE_DIR = DATA_DIR / "archive"
REPORTS_DIR = BASE_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Checkpoint file
CHECKPOINT_FILE = LOGS_DIR / "pipeline_checkpoint.json"

# Log file
LOG_FILE = LOGS_DIR / "pipeline_orchestrator.log"

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Pipeline steps configuration
PIPELINE_STEPS = [
    {
        'id': 'create_directories',
        'name': 'Create Required Directories',
        'function': 'create_directories',
        'required': True,
        'retry': False
    },
    {
        'id': 'scrape_hospitals',
        'name': 'Scrape Hospital Data',
        'script': 'hospital_scraper.py',
        'required': True,
        'retry': True,
        'max_retries': 2,
        'timeout': 1800  # 30 minutes
    },
    {
        'id': 'scrape_ambulances',
        'name': 'Scrape Ambulance Data',
        'script': 'ambulance_scraper.py',
        'required': True,
        'retry': True,
        'max_retries': 2,
        'timeout': 600  # 10 minutes
    },
    {
        'id': 'scrape_blood_banks',
        'name': 'Scrape Blood Bank Data',
        'script': 'blood_bank_scraper.py',
        'required': True,
        'retry': True,
        'max_retries': 2,
        'timeout': 600  # 10 minutes
    },
    {
        'id': 'generate_incidents',
        'name': 'Generate Incident Data',
        'script': 'incident_generator.py',
        'required': True,
        'retry': True,
        'max_retries': 2,
        'timeout': 600  # 10 minutes
    },
    {
        'id': 'preprocess_data',
        'name': 'Preprocess & Validate Data',
        'script': 'data_preprocessor.py',
        'required': True,
        'retry': True,
        'max_retries': 2,
        'timeout': 600  # 10 minutes
    },
    {
        'id': 'archive_raw_data',
        'name': 'Archive Raw Data',
        'function': 'archive_raw_data',
        'required': False,
        'retry': False
    },
    {
        'id': 'generate_summary',
        'name': 'Generate Pipeline Summary',
        'function': 'generate_summary',
        'required': True,
        'retry': False
    }
]

# ============================================================================
# CHECKPOINT MANAGEMENT
# ============================================================================

def load_checkpoint() -> Dict[str, Any]:
    """Load checkpoint from file."""
    if CHECKPOINT_FILE.exists():
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load checkpoint: {e}")
    return {'completed_steps': [], 'failed_steps': []}


def save_checkpoint(checkpoint: Dict[str, Any]):
    """Save checkpoint to file."""
    try:
        CHECKPOINT_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(checkpoint, f, indent=2)
    except Exception as e:
        logger.error(f"Could not save checkpoint: {e}")


def clear_checkpoint():
    """Clear checkpoint file."""
    try:
        if CHECKPOINT_FILE.exists():
            CHECKPOINT_FILE.unlink()
            logger.info("Checkpoint cleared")
    except Exception as e:
        logger.warning(f"Could not clear checkpoint: {e}")


# ============================================================================
# RESOURCE MONITORING
# ============================================================================

def get_system_stats() -> Dict[str, Any]:
    """Get current system resource usage."""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage(str(BASE_DIR))
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
    except Exception as e:
        logger.warning(f"Could not get system stats: {e}")
        return {}


# ============================================================================
# DIRECTORY MANAGEMENT
# ============================================================================

def create_directories() -> Dict[str, Any]:
    """Create all required directories."""
    logger.info("Creating required directories...")
    
    directories = [
        DATA_DIR,
        RAW_DIR,
        PROCESSED_DIR,
        ARCHIVE_DIR,
        REPORTS_DIR,
        LOGS_DIR
    ]
    
    created = []
    for directory in directories:
        if not directory.exists():
            directory.mkdir(parents=True, exist_ok=True)
            created.append(str(directory))
            logger.info(f"Created: {directory}")
        else:
            logger.info(f"Already exists: {directory}")
    
    return {
        'status': 'success',
        'created_directories': created,
        'total_directories': len(directories)
    }


# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

def run_script(script_name: str, timeout: int = 600, retry: bool = True, 
               max_retries: int = 2) -> Dict[str, Any]:
    """
    Run a Python script with timeout and retry logic.
    
    Args:
        script_name: Name of the script to run
        timeout: Timeout in seconds
        retry: Whether to retry on failure
        max_retries: Maximum number of retries
    
    Returns:
        Dictionary with execution results
    """
    script_path = SCRIPTS_DIR / script_name
    
    if not script_path.exists():
        return {
            'status': 'failed',
            'error': f'Script not found: {script_path}'
        }
    
    result = {
        'script': script_name,
        'attempts': 0,
        'status': 'pending'
    }
    
    attempt = 0
    while attempt <= (max_retries if retry else 0):
        attempt += 1
        result['attempts'] = attempt
        
        logger.info(f"Running {script_name} (attempt {attempt}/{max_retries + 1})...")
        
        start_time = time.time()
        
        try:
            # Run script as subprocess
            process = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(SCRIPTS_DIR),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = time.time() - start_time
            result['duration'] = duration
            result['return_code'] = process.returncode
            
            if process.returncode == 0:
                result['status'] = 'success'
                logger.info(f"✅ {script_name} completed successfully in {duration:.2f}s")
                return result
            else:
                result['status'] = 'failed'
                result['error'] = f"Non-zero exit code: {process.returncode}"
                result['stderr'] = process.stderr[-500:] if process.stderr else ''
                logger.error(f"❌ {script_name} failed with code {process.returncode}")
                
                if attempt <= max_retries and retry:
                    logger.info(f"Retrying {script_name}...")
                    time.sleep(5)  # Wait before retry
                else:
                    return result
                    
        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            result['duration'] = duration
            result['status'] = 'timeout'
            result['error'] = f'Timeout after {timeout}s'
            logger.error(f"⏱  {script_name} timed out after {timeout}s")
            
            if attempt <= max_retries and retry:
                logger.info(f"Retrying {script_name}...")
                time.sleep(5)
            else:
                return result
                
        except Exception as e:
            duration = time.time() - start_time
            result['duration'] = duration
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"❌ {script_name} error: {e}", exc_info=True)
            
            if attempt <= max_retries and retry:
                logger.info(f"Retrying {script_name}...")
                time.sleep(5)
            else:
                return result
    
    return result


# ============================================================================
# DATA ARCHIVAL
# ============================================================================

def archive_raw_data() -> Dict[str, Any]:
    """Archive raw data to backup folder."""
    logger.info("Archiving raw data...")
    
    if not RAW_DIR.exists():
        return {
            'status': 'skipped',
            'reason': 'Raw data directory not found'
        }
    
    # Create archive directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = ARCHIVE_DIR / f"raw_data_{timestamp}"
    
    try:
        shutil.copytree(RAW_DIR, archive_path)
        
        # Get archive size
        total_size = sum(
            f.stat().st_size for f in archive_path.rglob('*') if f.is_file()
        )
        
        logger.info(f"✅ Raw data archived to: {archive_path}")
        logger.info(f"   Archive size: {total_size / (1024**2):.2f} MB")
        
        return {
            'status': 'success',
            'archive_path': str(archive_path),
            'archive_size_mb': total_size / (1024**2),
            'timestamp': timestamp
        }
        
    except Exception as e:
        logger.error(f"❌ Archive failed: {e}", exc_info=True)
        return {
            'status': 'failed',
            'error': str(e)
        }


# ============================================================================
# SUMMARY GENERATION
# ============================================================================

def generate_summary(pipeline_results: Dict[str, Any]) -> Dict[str, Any]:
    """Generate pipeline summary."""
    logger.info("Generating pipeline summary...")
    
    summary = {
        'pipeline_execution': {
            'start_time': pipeline_results.get('start_time'),
            'end_time': pipeline_results.get('end_time'),
            'total_duration': pipeline_results.get('total_duration'),
            'total_steps': pipeline_results.get('total_steps'),
            'completed_steps': pipeline_results.get('completed_steps'),
            'failed_steps': pipeline_results.get('failed_steps'),
            'success_rate': pipeline_results.get('success_rate')
        },
        'step_results': pipeline_results.get('step_results', []),
        'system_stats': {
            'initial': pipeline_results.get('initial_stats', {}),
            'final': get_system_stats()
        }
    }
    
    # Check data files
    summary['data_files'] = {}
    
    # Raw data files
    raw_files = list(RAW_DIR.glob('*.csv')) if RAW_DIR.exists() else []
    summary['data_files']['raw'] = {
        'count': len(raw_files),
        'files': [
            {
                'name': f.name,
                'size_mb': f.stat().st_size / (1024**2),
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in raw_files
        ]
    }
    
    # Processed data files
    processed_files = list(PROCESSED_DIR.glob('*.csv')) if PROCESSED_DIR.exists() else []
    summary['data_files']['processed'] = {
        'count': len(processed_files),
        'files': [
            {
                'name': f.name,
                'size_mb': f.stat().st_size / (1024**2),
                'modified': datetime.fromtimestamp(f.stat().st_mtime).isoformat()
            }
            for f in processed_files
        ]
    }
    
    # Save summary to JSON
    summary_file = REPORTS_DIR / "pipeline_summary.json"
    try:
        summary_file.parent.mkdir(parents=True, exist_ok=True)
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"✅ Summary saved to: {summary_file}")
    except Exception as e:
        logger.error(f"❌ Could not save summary: {e}")
    
    # Generate HTML report
    generate_html_report(summary)
    
    return {
        'status': 'success',
        'summary_file': str(summary_file)
    }


def generate_html_report(summary: Dict[str, Any]):
    """Generate HTML pipeline report."""
    html_file = REPORTS_DIR / "pipeline_report.html"
    
    # Extract data
    exec_data = summary.get('pipeline_execution', {})
    steps = summary.get('step_results', [])
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ARIA Pipeline Execution Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0 0 10px 0;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .card h3 {{
            margin-top: 0;
            color: #667eea;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }}
        .success {{ color: #28a745; }}
        .error {{ color: #dc3545; }}
        .warning {{ color: #ffc107; }}
        table {{
            width: 100%;
            background: white;
            border-collapse: collapse;
            margin: 20px 0;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #667eea;
            color: white;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 0.9em;
            font-weight: bold;
        }}
        .badge-success {{ background: #d4edda; color: #155724; }}
        .badge-error {{ background: #f8d7da; color: #721c24; }}
        .badge-warning {{ background: #fff3cd; color: #856404; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: white;
            border-radius: 10px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 ARIA Pipeline Execution Report</h1>
        <p>End-to-End Data Pipeline Status</p>
        <p>Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>
    
    <div class="summary-cards">
        <div class="card">
            <h3>⏱️ Total Duration</h3>
            <div class="stat-value">{exec_data.get('total_duration', 0):.0f}s</div>
        </div>
        <div class="card">
            <h3>✅ Completed Steps</h3>
            <div class="stat-value success">{exec_data.get('completed_steps', 0)}</div>
        </div>
        <div class="card">
            <h3>❌ Failed Steps</h3>
            <div class="stat-value error">{exec_data.get('failed_steps', 0)}</div>
        </div>
        <div class="card">
            <h3>📊 Success Rate</h3>
            <div class="stat-value">{exec_data.get('success_rate', 0):.1f}%</div>
        </div>
    </div>
    
    <div class="card">
        <h2>Pipeline Steps</h2>
        <table>
            <tr>
                <th>Step</th>
                <th>Status</th>
                <th>Duration</th>
                <th>Details</th>
            </tr>
"""
    
    # Add step rows
    for step in steps:
        status = step.get('status', 'unknown')
        badge_class = 'badge-success' if status == 'success' else 'badge-error'
        duration = step.get('duration', 0)
        
        html_content += f"""
            <tr>
                <td><strong>{step.get('name', 'Unknown')}</strong></td>
                <td><span class="badge {badge_class}">{status.upper()}</span></td>
                <td>{duration:.2f}s</td>
                <td>{step.get('error', '-') if status != 'success' else '✓ Completed'}</td>
            </tr>
"""
    
    html_content += """
        </table>
    </div>
    
    <div class="footer">
        <p><strong>ARIA Emergency Response Platform</strong></p>
        <p>Phase 1 Data Pipeline v1.0</p>
    </div>
</body>
</html>
"""
    
    try:
        with open(html_file, 'w') as f:
            f.write(html_content)
        logger.info(f"✅ HTML report saved to: {html_file}")
    except Exception as e:
        logger.error(f"❌ Could not save HTML report: {e}")


# ============================================================================
# PIPELINE EXECUTION
# ============================================================================

def run_pipeline(resume: bool = False, force: bool = False) -> Dict[str, Any]:
    """
    Run the complete data pipeline.
    
    Args:
        resume: Resume from last checkpoint
        force: Force re-run of all steps
    
    Returns:
        Pipeline execution results
    """
    logger.info("=" * 70)
    logger.info("ARIA PIPELINE ORCHESTRATOR")
    logger.info("=" * 70)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize results
    results = {
        'start_time': datetime.now().isoformat(),
        'total_steps': len(PIPELINE_STEPS),
        'completed_steps': 0,
        'failed_steps': 0,
        'step_results': [],
        'initial_stats': get_system_stats()
    }
    
    # Load checkpoint if resuming
    checkpoint = load_checkpoint() if resume and not force else {'completed_steps': [], 'failed_steps': []}
    
    if force and CHECKPOINT_FILE.exists():
        clear_checkpoint()
        logger.info("🔄 Force mode: Starting fresh")
    elif resume and checkpoint.get('completed_steps'):
        logger.info(f"🔄 Resuming from checkpoint: {len(checkpoint['completed_steps'])} steps completed")
    
    # Progress bar
    if TQDM_AVAILABLE:
        pbar = tqdm(total=len(PIPELINE_STEPS), desc="Pipeline Progress", unit="step")
    else:
        pbar = None
    
    # Execute pipeline steps
    for step_config in PIPELINE_STEPS:
        step_id = step_config['id']
        step_name = step_config['name']
        
        # Skip if already completed (unless force)
        if not force and step_id in checkpoint.get('completed_steps', []):
            logger.info(f"⏭️  Skipping {step_name} (already completed)")
            results['completed_steps'] += 1
            if pbar:
                pbar.update(1)
            continue
        
        logger.info("")
        logger.info("─" * 70)
        logger.info(f"📍 Step: {step_name}")
        logger.info("─" * 70)
        
        step_start = time.time()
        step_result = {
            'id': step_id,
            'name': step_name,
            'start_time': datetime.now().isoformat()
        }
        
        try:
            # Execute step
            if 'script' in step_config:
                # Run script
                exec_result = run_script(
                    script_name=step_config['script'],
                    timeout=step_config.get('timeout', 600),
                    retry=step_config.get('retry', True),
                    max_retries=step_config.get('max_retries', 2)
                )
                step_result.update(exec_result)
            
            elif 'function' in step_config:
                # Run function
                func_name = step_config['function']
                if func_name == 'create_directories':
                    func_result = create_directories()
                elif func_name == 'archive_raw_data':
                    func_result = archive_raw_data()
                elif func_name == 'generate_summary':
                    func_result = generate_summary(results)
                else:
                    func_result = {'status': 'error', 'error': f'Unknown function: {func_name}'}
                
                step_result.update(func_result)
            
            # Calculate duration
            step_result['duration'] = time.time() - step_start
            step_result['end_time'] = datetime.now().isoformat()
            
            # Check status
            if step_result.get('status') == 'success':
                results['completed_steps'] += 1
                checkpoint['completed_steps'].append(step_id)
                logger.info(f"✅ {step_name} completed")
            else:
                results['failed_steps'] += 1
                checkpoint['failed_steps'].append(step_id)
                logger.error(f"❌ {step_name} failed")
                
                # Stop if required step fails
                if step_config.get('required', False):
                    logger.error("❌ Required step failed. Stopping pipeline.")
                    step_result['pipeline_stopped'] = True
                    results['step_results'].append(step_result)
                    break
            
            results['step_results'].append(step_result)
            save_checkpoint(checkpoint)
            
            if pbar:
                pbar.update(1)
                
        except Exception as e:
            logger.error(f"❌ Step error: {e}", exc_info=True)
            step_result['status'] = 'error'
            step_result['error'] = str(e)
            step_result['duration'] = time.time() - step_start
            results['failed_steps'] += 1
            results['step_results'].append(step_result)
            
            if step_config.get('required', False):
                logger.error("❌ Required step failed. Stopping pipeline.")
                break
    
    if pbar:
        pbar.close()
    
    # Final results
    results['end_time'] = datetime.now().isoformat()
    results['total_duration'] = (
        datetime.fromisoformat(results['end_time']) - 
        datetime.fromisoformat(results['start_time'])
    ).total_seconds()
    results['success_rate'] = (
        results['completed_steps'] / results['total_steps'] * 100
        if results['total_steps'] > 0 else 0
    )
    
    logger.info("")
    logger.info("=" * 70)
    logger.info("PIPELINE COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Total duration: {results['total_duration']:.2f}s")
    logger.info(f"Completed steps: {results['completed_steps']}/{results['total_steps']}")
    logger.info(f"Failed steps: {results['failed_steps']}")
    logger.info(f"Success rate: {results['success_rate']:.2f}%")
    logger.info("=" * 70)
    
    # Clear checkpoint if fully successful
    if results['failed_steps'] == 0:
        clear_checkpoint()
    
    return results


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='ARIA Pipeline Orchestrator - End-to-end data pipeline execution'
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help='Resume from last checkpoint'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force re-run all steps (ignore checkpoint)'
    )
    
    args = parser.parse_args()
    
    try:
        results = run_pipeline(resume=args.resume, force=args.force)
        
        # Exit code based on results
        if results['failed_steps'] == 0:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Pipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
