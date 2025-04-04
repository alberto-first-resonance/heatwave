from setuptools import setup, find_packages

setup(
    name="pr_files_exporter",
    version="0.1.0",
    description="GitHub PR Files Exporter - Analyze GitHub pull requests and generate file change reports",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/pr-files-exporter",
    packages=find_packages(),
    scripts=["pr_files_export.py"],
    install_requires=[
        "requests>=2.31.0",
    ],
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Version Control :: Git",
    ],
) 