from setuptools import setup, find_packages

with open('requirements.txt') as f:
	install_requires = f.read().strip().split('\n')

# get version from __version__ variable in qp_phonix_front/__init__.py
from qp_phonix_front import __version__ as version

setup(
	name='qp_phonix_front',
	version=version,
	description='Phonix Front',
	author='Rafael Licett',
	author_email='rafael.licett@mentum.group',
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
