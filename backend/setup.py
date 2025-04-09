from setuptools import setup, find_packages

setup(
    name="ai_notes_generator",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pydantic",
        "PyPDF2",
        "openai",
    ],
) 