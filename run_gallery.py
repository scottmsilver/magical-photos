#!/usr/bin/env python3
"""
Launch the Magical Portrait Gallery web server.

This creates a web interface to display your generated magical portraits
with interactive features.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from gallery.app import main

if __name__ == "__main__":
    main()
