import sys
import os

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import PhotoPilotApp


def main() -> None:
    app = PhotoPilotApp()
    app.run()


if __name__ == "__main__":
    main()
