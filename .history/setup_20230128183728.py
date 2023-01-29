from setuptools import setup

setup(
   name='PIhexapod',
   version='0.1.0',
   author='Byeongdu Lee',
   author_email='blee@anl.gov',
   packages=['pihexapod'],
   url='#',
   license='LICENSE.txt',
   description='EPICS and pipython tool for defining a user coordinate system of PI hexapod C-887',
   install_requires=[
       "pyepics",
       "pipython",
   ],
)