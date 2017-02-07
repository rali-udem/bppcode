from setuptools import setup

setup(name='bppgen',
      version='0.1',
      description='Text generator for BPPProject',
      url='',
      author='Philippe Bighouse',
      author_email='phil.bighouse@gmail.com',
      license='MIT',
      package_dir = {
            'bppgen' : 'bppgen',
                'bppgen.letter' : 'bppgen/letter',
                'bppgen.api' : 'bppgen/api',
                'bppgen.data' : 'bppgen/data'},
      packages=['bppgen',
                'bppgen.letter',
                'bppgen.api',
                'bppgen.data'],
      install_requires=[
          'flask', 'six', 'certifi', 'gentext', 'langid'
      ],
      zip_safe=True)