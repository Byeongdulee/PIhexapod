# PIhexapod
A small python package to define and remove your own coordination system for PI hexapod (C-887 controller)

## Introduction
This is written to define a sample coordinate for the PI hexapod when connecting it through EPICS. It uses asyn record to send and receive GCS command to the controller. This can also be used to directly connect to it without using EPICS. In this case, it does that with PIPYTHON package.


## Usage
```python
from PIhexapod.gcs import hexapod
h = hexapod('12idHXP')

# list all coordination system defined for the hexapod
h.get_allcs()

# get currently activate coordinate system
h.get_CS()

# make a sample coordinate of which reference coordinate is ZERO
h.add_CS(csname='NEWCS', X=0, Y=10, Z=100, U=30, V=0, W=0, parent='ZERO')

# redefine the Y position of NEWCS
h.set_CSpos(csname='NEWCS', Y=100)

# Activate NEWCS
h.set_CS('NEWCS')

# read positions of my sample coordinate system.
h.get_mycsinfo()

# Remove NEWCS
h.remove_CS('NEWCS')