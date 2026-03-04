import os
from pathlib import Path

# ensure tests always run with the project root as the working directory
# so relative paths like "examples/small_college.json" resolve correctly
os.chdir(Path(__file__).parent)
