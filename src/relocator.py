import os
import shutil
import logging

logger = logging.getLogger(__name__)


def move_nc_files(source_directory, target_directory):
    # Create the target directory if it doesn't exist
    os.makedirs(target_directory, exist_ok=True)

    # Get the list of files in the source directory
    files = os.listdir(source_directory)

    # Move files with the '.nc' extension to the target directory
    for filename in files:
        if filename.endswith(".nc"):
            source_path = os.path.join(source_directory, filename)
            target_path = os.path.join(target_directory, filename)
            shutil.move(source_path, target_path)


def main():
    target_directory = os.path.join(os.getcwd(), "data_nc")
    source_directory = os.getcwd()
    move_nc_files(source_directory, target_directory)


if __name__ == "__main__":
    main()
    logger.warning("Process status: Success")
