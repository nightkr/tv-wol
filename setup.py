from setuptools import setup

setup(
    name='tv-wol',
    version='0.1',
    packages=['tv_wol'],
    entry_points={
        'console_scripts': ['tv-wol=tv_wol:main']
    },
    install_requires=['cec'],
    zip_safe=False
)
