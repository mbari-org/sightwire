import os

def rename_frames(directory, new_directory):
    # Check if the directory exists
    if not os.path.exists(directory):
        print(f"The directory '{directory}' does not exist.")
        return

    # Get a list of files in the directory
    files = os.listdir(directory)

    # Filter only image files (you can adjust the extension based on your actual file format)
    image_files = [file for file in files if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Sort the image files
    image_files.sort()

    # Rename the files to follow the pattern frame_%04d.jpg
    for i, image_file in enumerate(image_files):
        new_name = f"frame_{i:04d}.png"
        old_path = os.path.join(directory, image_file)
        new_path = os.path.join(new_directory, new_name)

        # Rename the file
        os.rename(old_path, new_path)
        print(f"Renamed: {old_path} -> {new_path}")

if __name__ == "__main__":
    frames_directory = '/Users/dcline/Dropbox/code/sightwire/tator/compas/P_R_PNG'
    new_directory = '/Users/dcline/Dropbox/code/sightwire/tator/compas/P_R_PNG_'
    rename_frames(frames_directory, new_directory)
