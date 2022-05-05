from setuptools import setup, find_packages


def read_requirements(file):
    with open(file) as f:
        return f.read().splitlines()


inst_reqs = read_requirements("requirements.txt")

setup(
    name='eo_custom_scripts',
    version='0.1',
    packages=find_packages(exclude=["tests"]),
    inst_reqs=inst_reqs,
    url='',
    license='',
    author='John Lavelle',
    author_email='jlavelle@compass.ie',
    description='Call the Sentinel-Hub API on the command line and write to S£'
)
