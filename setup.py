import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygsgui",
    version="1.0.0",
    author="StupidDeveloper05",
    author_email="StupidDeveloper05@gmail.com",
    description="This my first Python Game Super Graphic User Interface!!!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StupidDeveloper05/pygsgui",
    packages=setuptools.find_packages(),
    package_data={'pygsgui': ['basicTheme.json']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pillow',
        'overrides',
        'keyboard'
      ],
    python_requires='>=3.6',
)