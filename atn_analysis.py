import os
import subprocess


from config import ATN_ANALYSIS_INPUT_DIRECTORY, ATN_ANALYSIS_OUTPUT_DIRECTORY
from print import print_progress_bar


def convert_dot_to_png(dot_directory, png_directory):
    """
        Converts all dot files in a directory to pngs and saves them in a given directory.

        Args:
            dot_directory (str): The directory to convert.
            png_directory (str): The directory to save the pngs.
    """

    output_directory = png_directory
    os.makedirs(output_directory, exist_ok=True)

    total_amount_of_dot_files = len([name for name in os.listdir(dot_directory) if name.endswith('.dot')])
    amount_of_dot_files = 0
    for filename in os.listdir(dot_directory):
        if filename.endswith('.dot'):
            amount_of_dot_files += 1

            dot_file_path = os.path.join(dot_directory, filename)
            png_file_path = os.path.join(output_directory, f"{os.path.splitext(filename)[0]}.png")

            command = ['dot', '-Tpng', dot_file_path, '-o', png_file_path]

            try:
                subprocess.run(command, check=True, shell=True)
                print_progress_bar(amount_of_dot_files, total_amount_of_dot_files, length=40)
            except Exception as e:
                print(f"Failed to convert {filename}: {e}")

    if amount_of_dot_files == 0:
        print("⚠️ No ATNs found! Do you generated the parser with the '-atn' tool option?")


if __name__ == "__main__":
    print("ℹ️ The parser should have atn activated (generated with -atn tool option)")

    input_directory = ATN_ANALYSIS_INPUT_DIRECTORY
    output_directory = ATN_ANALYSIS_OUTPUT_DIRECTORY

    if os.path.isdir(input_directory) and os.path.isdir(output_directory):
        convert_dot_to_png(input_directory, output_directory)
    else:
        print("Invalid directory. Please check the path and try again.")
