from setuptools import find_packages, setup


def load(filename):
    return open(filename, "rb").read().decode("utf-8")


version_info = {}
exec(open("werkit/package_version.py").read(), version_info)


setup(
    name="werkit",
    version=version_info["__version__"],
    description="Toolkit for encapsulating Python-based computation into deployable and distributable tasks",
    long_description=load("README.md"),
    long_description_content_type="text/markdown",
    author="Metabolize",
    author_email="github@paulmelnikow.com",
    url="https://github.com/metabolize/werkit",
    project_urls={
        "Issue Tracker": "https://github.com/metabolize/werkit/issues",
        "Documentation": "https://werkit.readthedocs.io/en/stable/",
    },
    packages=find_packages(),
    install_requires=load("requirements.txt"),
    extras_require={"client": load("requirements_client.txt")},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: System :: Distributed Computing",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
)
