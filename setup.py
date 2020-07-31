import setuptools


def main():
  with open('README.md', 'r') as fp:
    readme = fp.read()

  setuptools.setup(
    name='latexify-py',
    version='0.0.5',
    description='Generates LaTeX source from Python functions.',
    long_description=readme,
    long_description_type='text/markdown',
    url='https://github.com/odashi/latexify_py',
    author='Yusuke Oda',
    author_email='yus.takara@gmail.com',
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
