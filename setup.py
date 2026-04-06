from setuptools import setup, find_packages

setup(
    name="log",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=2.2.6",
        "markdown-it-py>=4.0.0",
        "mdurl>=0.1.2",
        "Pygments>=2.20.0",
        "rich>=14.3.3",
        "setuptools>=82.0.1"
    ],
    entry_points={
        'console_scripts': [
            'log-filter = log.cli:main', 
        ],
    },
    author="Gabriel Rocha de Souza",
    author_email="souza.gabriel.0210@gmail.com",
    description="Codes used for terminal logging",
    url="https://github.com/Gabriel-br2/log.git"
)
