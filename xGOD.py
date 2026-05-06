import subprocess
import sys

# Launch the native iso2god binary (built from x_tool/iso2god-rs).
# Usage: x_tool/iso2god <source_iso> <output_dir>
if len(sys.argv) < 3:
    print("Usage: python3 xGOD.py <source_iso> <output_dir>")
    sys.exit(1)

iso_file = sys.argv[1]
output_dir = sys.argv[2]
subprocess.run(['x_tool/iso2god', iso_file, output_dir], check=True)
