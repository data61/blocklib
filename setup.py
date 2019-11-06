import setuptools

with open('README.rst', 'r', encoding='utf-8') as f:
    readme = f.read()


setuptools.setup(
    name="blocklib",
    version="0.0.2",
    author="Joyce Wang",
    author_email="joyce.wang@csiro.au",
    description="A library for blocking in record linkage",
    long_description=readme,
    long_description_content_type='text/x-rst',
    url='https://github.com/data61/blocklib',
    license='Apache',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "Fuzzy>=1.2"
    ],
    tests_require=[
        "pytest>=5.0",
    ]
)
