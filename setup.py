import os
import shutil
import glob
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

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
    "dask[dataframe]",
    "fastparquet",
]

# Copy script files
plugins_folder = os.path.join(os.path.expanduser("~"), ".countess/")
os.makedirs(plugins_folder, exist_ok=True)
for file in glob.glob("plugins/*.py"):
    shutil.copy(file, plugins_folder)
for file in glob.glob("plugins/*.txt"):
    shutil.copy(file, plugins_folder)

setuptools.setup(
    name="CountESS",
    version="0.0.1",
    author="Alan F Rubin",
    author_email="alan.rubin@wehi.edu.au",
    description="Analysis program for calculating variant scores from "
    "deep mutational scanning data.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/countess-project/countess",
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": ["enrich_cmd = countess.main:main_cmd"],
        "gui_scripts": ["enrich_gui = countess.main:main_gui"],
    },
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
    test_suite="tests",
)
