""" setup module for Google Translate CLI """
import os
from setuptools import setup, find_packages, Command

VERSION = "1.0.0"

# Runtime dependencies. See requirements.txt for development dependencies.
DEPENDENCIES = [
    "google-cloud-translate",
]


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    @staticmethod
    def run():
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


setup(
    name='sytr',
    version=VERSION,
    description='CLI Google Translate',
    author='Dan Timofte',
    author_email='timoftedan@gmail.com',
    url='https://github.com/dantimofte/gtranslate',
    packages=find_packages(),
    install_requires=DEPENDENCIES,
    include_package_data=True,
    keywords=[],
    classifiers=[],
    zip_safe=True,
    cmdclass={
        'clean': CleanCommand,
    },
    entry_points={
        "console_scripts": [
            "gtranslate = sytr.tools.cli:main",
        ],
    }
)
