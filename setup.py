import os
import sys
import shutil
import glob
from setuptools import setup, find_packages

requirements = [
    "numpy >= 1.10.4",
    "scipy >= 0.16.0",
    "pandas >= 0.18.0",
    "statsmodels >= 0.6.1",
    "matplotlib >= 1.4.3",
    "pyyaml >= 3.12",
    "sphinx_rtd_theme",
    "sphinx >= 1.5.6",
    "tables >= 3.2.0",
]

# Copy script files
plugins_folder = os.path.join(os.path.expanduser("~"), ".enrich2/")
os.makedirs(plugins_folder, exist_ok=True)
for file in glob.glob("plugins/*.py"):
    shutil.copy(file, plugins_folder)
for file in glob.glob("plugins/*.txt"):
    shutil.copy(file, plugins_folder)

setup(
    name="Enrich2",
    version="2.0.0",
    packages=find_packages(),
    package_data={"enrich2.tests": ["data/*/*/*"],},
    entry_points={
        "console_scripts": ["enrich_cmd = enrich2.main:main_cmd"],
        "gui_scripts": ["enrich_gui = enrich2.main:main_gui"],
    },
    test_suite="enrich2.tests.test_enrich2",
    author="Alan F Rubin",
    author_email="alan.rubin@wehi.edu.au",
    description="Analysis program for calculating variant scores from "
    "deep mutational scanning data.",
    url="https://github.com/FowlerLab/Enrich2/",
    install_requires=requirements,
)
