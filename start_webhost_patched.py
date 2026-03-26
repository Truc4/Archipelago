#!/usr/bin/env python3
import sys
import os

# Patch ALTTP sprite loading to skip ROM requirement
import WebHostLib.lttpsprites
WebHostLib.lttpsprites.update_sprites_lttp = lambda: None

# Now run WebHost normally
if __name__ == "__main__":
    from WebHostLib import app
    from waitress import serve
    
    import logging
    logging.basicConfig(
        format="[%(asctime)s] %(message)s",
        level=logging.INFO
    )
    
    print("="*60)
    print("WebHost Starting on http://0.0.0.0:5000")
    print("="*60)
    
    serve(
        app,
        host="0.0.0.0",
        port=5000,
        threads=10,
        url_scheme="http"
    )
