from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='tavily-python',
    version='0.7.8',
    url='https://github.com/tavily-ai/tavily-python',
    author='Tavily AI',
    author_email='support@tavily.com',
    description='Python wrapper for the Tavily API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['tests']),
    install_requires=['requests', 'tiktoken>=0.5.1', 'httpx'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
