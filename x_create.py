import os
import subprocess
import sys

def contains_xex_or_xbe(directory):
    """Check if a directory contains any .xex or .xbe files."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xex') or file.endswith('.xbe'):
                return True
    return False

def create_xiso_from_directories(source_dir, output_dir):
    all_dirs = [
        d for d in os.listdir(source_dir)
        if os.path.isdir(os.path.join(source_dir, d)) and contains_xex_or_xbe(os.path.join(source_dir, d))
    ]
    total_dirs = len(all_dirs)

    if total_dirs == 0:
        print("NO FOLDER DIRECTORIES WITH .xex or .xbe FILES FOUND.")
        return

    print(f"FOUND {total_dirs} FOLDER DIRECTORIES TO PROCESS.\n")

    for dir_name in all_dirs:
        iso_filename = os.path.join(output_dir, f"{dir_name}.iso")
        game_dir = os.path.join(source_dir, dir_name)

        if os.path.isfile(iso_filename):
            print(f"SKIPPING: \nFILE EXISTS> {iso_filename}")
            continue

        print(f"Game Folder: \n{dir_name}")

        result = subprocess.run(
            ["x_tool/extract-xiso", "-c", game_dir, iso_filename],
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"\nError CREATING ISO for \n{dir_name}\n")
            print(f"\nCommand output: \n{result.stdout}\n")
            print(f"\nCommand error: \n{result.stderr}\n")
        else:
            print(f"SUCCESS \n{iso_filename}\n")

    print("\nDONE.\n")

if __name__ == "__main__":
    create_xiso_from_directories(sys.argv[1], sys.argv[2])
