from setuptools import setup, find_packages

with open('README.rst', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tavily-python',
    version='0.1.9',
    url='https://github.com/assafelovic/tavily-python',
    author='Assaf Elovic',
    author_email='assaf.elovic@gmail.com',
    description='Python wrapper for the Tavily API',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(),
    install_requires=['requests'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
