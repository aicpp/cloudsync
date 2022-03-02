from setuptools import setup
from setuptools.command.install import install
from pathlib import Path


class CreateLocalStateDir(install):
    """
    Creates a local state directory to store
    hashes, source and target files, keys, etc.
    """

    def run(self):
        home = Path.home() / ".cloudsync"
        home.mkdir(parents=True, exist_ok=True)
        install.run(self)


setup(
    name='cloudsync',
    version='0.1',
    description='A useful module',
    author='aicpp(https://github.com/aicpp), Kyle Barry',
    packages=['cloudsync'],
    install_requires=['dropbox'],
    cmdclass={'install': CreateLocalStateDir},
)
