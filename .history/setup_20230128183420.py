from setuptools import setup

setup(
   name='PIhexapod',
   version='0.1.0',
   author='Byeongdu Lee',
   author_email='blee@anl.gov',
   packages=['pihexapod', 'pihexapod.test'],
   url='http://pypi.python.org/pypi/PIhexapod/',
   license='LICENSE.txt',
   description='EPICS and pipython tool for defining a user coordinate system of PI hexapod C-887',
   long_description=open('.README.md').read(),
   install_requires=[
       "pyepics",
       "pipython",
   ],
)