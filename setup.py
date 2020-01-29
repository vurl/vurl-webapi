from setuptools import setup


dependencies = [
    'yhttp >= 2.5, < 3',
    'redis',
]


setup(
    name='vurl',
    version='0.1',
    description='Url shortener web application',
    long_description=open('README.md').read(),
    install_requires=dependencies,
    py_modules=['vurl'],
    entry_points=dict(console_scripts='vurl=vurl:app.climain'),
    license='MIT',
)
