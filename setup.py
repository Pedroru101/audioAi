from setuptools import setup, find_packages

setup(
    name="meeting_assistant",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        # Lista de dependencias básicas
        'PyQt5>=5.15',
        'plyer>=2.0',
        'requests>=2.28',
    ],
)
