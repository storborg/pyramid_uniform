from setuptools import setup


setup(name='pyramid_uniform',
      version='0.2',
      description='Form handling for Pyramid.',
      long_description='',
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Framework :: Pyramid',
      ],
      keywords='pyramid forms validation rendering',
      url='http://github.com/cartlogic/pyramid_uniform',
      author='Scott Torborg',
      author_email='scott@cartlogic.com',
      install_requires=[
          'Pyramid',
          'FormEncode',
          'webhelpers2',
          'six',
          # These are for tests.
          'coverage',
          'nose>=1.1',
          'nose-cover3',
      ],
      license='MIT',
      packages=['pyramid_uniform'],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
