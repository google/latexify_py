import io
from setuptools import setup
from setuptools import find_packages


with io.open('README.md', 'rt', encoding='utf8') as f:
  readme = f.read()


setup(
  name='Latexify',
  url='https://github.com/odashi/latexify_py',
  packages=find_packages(),
  license='Apache License 2.0',
  author='Yusuke Oda',
  description='Generates LaTeX math description from Python functions.',
  long_description=readme,
  python_requires='>=3.6, <3.9',
  tests_require=['pytest']
)
