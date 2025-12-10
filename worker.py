#!/usr/bin/env python3
"""
Worker startup script for development purposes.
In production, use the Docker Compose setup or run:
celery -A app.core.celery_app worker --loglevel=info
"""

import os
import sys
import subprocess

def start_worker():
    """Start the Celery worker"""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Start the Celery worker
        subprocess.run([
            sys.executable, "-m", "celery",
            "-A", "app.core.celery_app",
            "worker",
            "--loglevel=info"
        ])
    except KeyboardInterrupt:
        print("Worker stopped.")
    except Exception as e:
        print(f"Error starting worker: {e}")

if __name__ == "__main__":
    start_worker()