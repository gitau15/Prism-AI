#!/usr/bin/env python3
"""
Flower monitoring tool startup script for development purposes.
In production, use the Docker Compose setup or run:
celery -A app.core.celery_app flower
"""

import os
import sys
import subprocess

def start_flower():
    """Start the Flower monitoring tool"""
    try:
        # Change to the project directory
        project_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_dir)
        
        # Start Flower
        subprocess.run([
            sys.executable, "-m", "celery",
            "-A", "app.core.celery_app",
            "flower"
        ])
    except KeyboardInterrupt:
        print("Flower stopped.")
    except Exception as e:
        print(f"Error starting Flower: {e}")

if __name__ == "__main__":
    start_flower()