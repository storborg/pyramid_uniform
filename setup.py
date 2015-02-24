import sys
from setuptools import setup, find_packages

PY3 = sys.version_info[0] > 2


requires = [
    'Pyramid>=1.4.5',
    'webhelpers2==2.0b5',
    'six>=1.5.2',
    # These are for tests.
    'coverage',
    'nose>=1.1',
    'nose-cover3',
]

# NOTE: Once FormEncode 1.3 is non-alpha, just use it for all platforms.
if PY3:
    requires.append('FormEncode>=1.3.0a1')
else:
    requires.append('FormEncode>=1.2')


setup(name='pyramid_uniform',
      version='0.3.1',
      description='Form handling for Pyramid.',
      long_description='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Framework :: Pyramid',
      ],
      keywords='pyramid forms validation rendering',
      url='http://github.com/cartlogic/pyramid_uniform',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      install_requires=requires,
      license='MIT',
      packages=find_packages(),
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
