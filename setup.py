from setuptools import setup, find_packages

setup(
    name='pyrtc',
    version='0.1',
    license='MIT',
    description='An example Python package',
    url="https://github.com/hello-fazil/pyRTC",
    long_description=open('README.md').read(),
    install_requires=[
        'aiortc','numpy','opencv-python','aiohttp'
    ],
    packages=['pyrtc'], 
    author='Mohamed Fazil',
    author_email='mohamedfazilsulaiman@gmail.com',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
