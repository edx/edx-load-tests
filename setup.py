from setuptools import setup, find_packages
setup(
    name="edx-load-tests",
    packages=find_packages(),
    package_data={
        'settings_files': ['*.yml'],
    },
    entry_points = {
        'console_scripts': [
            'merge_settings = util.merge_settings:main',
            'generate_summary = util.generate_summary:main',
        ],
    },
    # minimal set of requirements only corresponding to the scripts in
    # entry_points.
    install_requires=["click", "PyYAML",],
)
