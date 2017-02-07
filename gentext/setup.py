from setuptools import setup

setup(name='gentext',
      version='0.1',
      description='Text generator',
      url='',
      author='Philippe Bighouse',
      author_email='phil.bighouse@gmail.com',
      license='MIT',
            package_dir = {
            'gentext' : 'gentext'},
      packages=['gentext'],
      install_requires=[
          'nltk', 'mock',
      ],
      zip_safe=True)