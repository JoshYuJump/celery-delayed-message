from setuptools import find_packages, setup

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

with open("version", "r") as fh:
    version = fh.read()

setup(
    name='celery-delayed-message',
    version=version,
    description='Real celery delayed message',
    url='https://github.com/JoshYuJump/celery-delayed-message',
    author='Josh.Yu',
    author_email='josh.yu_8@live.com',
    license='MIT',
    install_requires=install_requires,
    packages=find_packages(),
)
