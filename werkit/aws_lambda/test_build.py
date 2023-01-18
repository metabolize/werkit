from .build import create_venv_with_dependencies, site_packages_for_venv


def test_site_packages_for_venv(tmpdir):
    venv_dir = str(tmpdir / "venv")
    create_venv_with_dependencies(venv_dir, install_requirements_from=[])
    site_packages_dir = site_packages_for_venv(venv_dir)
    assert site_packages_dir.startswith(venv_dir)
    assert site_packages_dir.endswith("/site-packages")
