import re
from os.path import join, dirname

from setuptools import setup


# reading package's version (same way sqlalchemy does)
with open(join(dirname(__file__), 'vurl.py')) as f:
    version = re.match('.*__version__ = \'(.*?)\'', f.read(), re.S).group(1)


dependencies = [
    'yhttp >= 2.5, < 3',
    'redis',
]


setup(
    name='vurl',
    version=version,
    description='Url shortener web application',
    long_description=open('README.md').read(),
    install_requires=dependencies,
    py_modules=['vurl'],
    entry_points=dict(console_scripts='vurl=vurl:app.climain'),
    license='MIT',
)

