from setuptools import setup, find_packages

setup(
    name='SmashStats',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/is386/SmashStats/blob/refactor/smashstats.py',
    license='GPL',
    author='is386',
    author_email='',
    description='A Discord bot for Super Smash Bros. Ultimate frame data.',
    install_requires=['discord.py>=2.3.2,<3.0']
)
