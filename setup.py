from setuptools import setup, find_packages
setup(
    name="edx-load-tests",
    packages=find_packages(),
    package_data={
        'settings_files': ['*.yml'],
    },
)
