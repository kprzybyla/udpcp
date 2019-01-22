import os
import codecs

from setuptools import setup, find_packages


def main():

    with codecs.open('README.rst', encoding='utf-8') as handle:
        long_description = handle.read()

    setup(
        name='udpcp',
        author='Krzysztof Przybyła',
        url='https://github.com/kprzybyla/udpcp',
        description='UDPCP Protocol (Version 2) Library',
        long_description=long_description,
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Natural Language :: English',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Libraries',
            'Topic :: System :: Networking',
        ],
        install_requires=[
            'bitarray>=0.8.3',
        ],
        extras_require={
            'lint': [
                'flake8>=3.5.0',
            ],
            'mypy': [
                'mypy>=0.620'
            ],
            'test': [
                'pytest>=3.4.0',
                'pytest-cov>=2.5.1',
            ],
        },
        use_scm_version={
            'write_to': os.path.join('src/udpcp/_version.py'),
        },
        platforms=[
            'linux',
        ],
        setup_requires=[
            'setuptools_scm',
        ],
        packages=find_packages(where='src'),
        package_dir={
            '': 'src',
        },
    )


if __name__ == '__main__':
    main()
