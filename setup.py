from setuptools import setup, find_packages

setup(
    name='tavily-python',
    version='0.1.0',
    url='https://github.com/assafelovic/tavily-python',
    author='Assaf Elovic',
    author_email='assaf.elovic@gmail.com',
    description='Python wrapper for the Tavily API',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
