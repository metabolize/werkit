import os
import zipfile


def create_zipfile_from_dir(dir_path, path_to_zipfile):
    with zipfile.ZipFile(path_to_zipfile, "w", zipfile.ZIP_DEFLATED) as f:
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                fullpath = os.path.join(root, file)
                arcname = os.path.relpath(fullpath, start=dir_path)
                f.write(fullpath, arcname=arcname)
