from pathlib import Path
import os
import sys

if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent.parent)
    sys.path.insert(0, "")
    from cmdbox.app import app
    exit_code = app.main(webcall=True)
    exit(exit_code)
