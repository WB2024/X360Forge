import os
import subprocess

def extract_xiso_from_files(iso_folder, output_folder, delete_after=False):
    print(f"READING FOLDER: '{iso_folder}'...")

    # List all .iso files in the chosen folder
    iso_files = [f for f in os.listdir(iso_folder) if f.endswith('.iso')]

    if not iso_files:
        print("NO .iso FILES FOUND IN SELECTED FOLDER.")
        return

    for iso_file in iso_files:
        print(f"\nEXTRACTING: {iso_file}\n")

        iso_path = os.path.join(os.path.abspath(iso_folder), iso_file)
        result = subprocess.run(
            ["x_tool/extract-xiso", "-x", iso_path],
            capture_output=True,
            cwd=output_folder
        )

        iso_name = os.path.splitext(iso_file)[0]

        if result.returncode != 0:
            print(f"SKIPPING: \nFOLDER EXISTS> {iso_name}")
        else:
            print(f"SUCCESS: \n{iso_name}")

            if delete_after:
                print(f"\nDELETING: \n{iso_file}")
                os.remove(iso_path)

    print("\nDONE.\n")
