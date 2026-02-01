from setuptools import setup, find_packages

setup(
    name="inx-builder",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "Jinja2>=3.0",
        "pyyaml>=6.0",
        "click>=8.0",
    ],
    entry_points={
        "console_scripts": [
            "inx=inx_builder.cli:main",
            "inx-builder=inx_builder.cli:main",
        ],
    },
)
