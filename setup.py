import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='decal',
    version='0.0.1',
    description='A small declarative MicroPython GUI library for display drivers based on the FrameBuffer interface', # noqa: E501
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/submer-crypto/decal',
    license='ISC',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: OS Independent'
    ],
    python_requires='>=3.8',
)
