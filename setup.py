from setuptools import setup, find_packages

setup(
    name="FastTextProcessor",
    version="2.0.0",
    description="A tool for processing text data in various formats",
    author="Loh Yi Ling",
    author_email="lohyilingg0119@gmail.com",
    packages=find_packages(),
    install_requires=[
        "tqdm",
    ],
)
