from setuptools import setup, find_packages

setup(
    name='SmashStats',
    version='0.1',
    packages=find_packages(),
    url='https://github.com/1nderr/smash-stats-bot/blob/refactor/smashstats.py',
    license='GPL',
    author='1nder',
    author_email='',
    description='A Discord bot for Super Smash Bros. Ultimate frame data.',
    install_requires=['discord.py>=2.3.2,<3.0']
)
