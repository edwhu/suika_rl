from setuptools import setup, find_packages

setup(
    name='suika_rl',
    version='0.1.0',    # your package version
    packages=find_packages(where='suika_env'),
    package_dir={'': 'suika_env'},
    install_requires=[
        'gymnasium',  # and other necessary packages
        'selenium',
    ],
)