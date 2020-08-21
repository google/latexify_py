# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools


def main():
  with open('README.md', 'r') as fp:
    readme = fp.read()

  setuptools.setup(
    name='latexify-py',
    version='0.0.7',
    description='Generates LaTeX source from Python functions.',
    long_description=readme,
    long_description_type='text/markdown',
    url='https://github.com/google/latexify_py',
    author='Yusuke Oda',
    author_email='oday@google.com',
    license='Apache Software License 2.0',
    classifiers=[
        'Framework :: IPython',
        'Framework :: Jupyter',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Text Processing :: Markup :: LaTeX',
    ],
    keywords='equation latex math mathematics',
    packages=['latexify'],
    install_requires=[
        'dill>=0.3.2',
    ],
    python_requires='>=3.6, <3.9',
  )


main()
