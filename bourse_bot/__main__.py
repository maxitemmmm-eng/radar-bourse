import sys
from .main import main

if __name__ == "__main__":   # version 67 : indispensable pour les calculs en parallèle sous Windows
    sys.exit(main())
