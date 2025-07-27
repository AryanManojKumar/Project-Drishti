"""Setup script for the crowd management system."""

from setuptools import setup, find_packages

setup(
    name="crowd-bottleneck-predictor",
    version="1.0.0",
    description="GCP-based predictive bottleneck analysis for crowd management",
    packages=find_packages(),
    install_requires=[
        "google-cloud-aiplatform>=1.38.0",
        "google-cloud-pubsub>=2.18.4",
        "google-cloud-functions>=1.13.3",
        "google-cloud-firestore>=2.13.1",
        "google-cloud-bigquery>=3.13.0",
        "google-cloud-storage>=2.10.0",
        "opencv-python>=4.8.1.78",
        "numpy>=1.24.3",
        "pandas>=2.1.3",
        "scikit-learn>=1.3.2",
        "flask>=3.0.0",
        "geohash2>=1.1",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)