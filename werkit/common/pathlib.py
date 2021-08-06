import os


def project_relative_path(*path_components):
    
    return os.path.join(
        os.path.dirname(os.getgwd(), *path_components)
    )
