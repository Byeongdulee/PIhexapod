# PIhexapod
A small python package to define and remove your own coordination system for PI hexapod (C-887 controller)

## Introduction
This is written to define a sample coordinate for the PI hexapod when connecting it through EPICS. It uses asyn record to send and receive GCS command to the controller. This can also be used to directly connect to it without using EPICS. In this case, it does that with PIPYTHON package.

## Install
After cloning the package, run setup.py.
```
python setup.py install
```

## Usage
```python
from pihexapod.gcs import Hexapod, plot_record
# when your epics base is "12idHXP"
h = Hexapod('12idHXP')
# or, to connect directly to 'YOUR.IP.ADDRESS.NUMBER' without EPICS
h = Hexapod('YOUR.IP.ADDRESS.NUMBER')
# or, to get a help from InterfaceSetupDlg to find your device.
h = Hexapod('')

# list all coordination systems defined for the hexapod
h.get_allcs()

# get the currently activated coordinate system.
h.get_CS()

# make a sample coordinate system of which reference coordinate is ZERO
ax = h.get_axes()
ax['Z'] += 100
h.add_CS(csname='NEWCS', axes = ax, parent='ZERO')
```
or
```python
# set X=10 and Y=10, and the rest will be set to 0.
h.add_CS(csname='NEWCS', X=10, Y=10, parent='ZERO')

# redefine only the Y position of NEWCS
h.set_CSpos(csname='NEWCS', Y=100)
```
or
```python
# activate NEWCS
h.set_CS('NEWCS')

# read the positions of my sample coordinate system.
h.get_mycsinfo('NEWCS')

# Remove NEWCS
h.remove_CS('NEWCS')
```
Trajectory scan can be done with a beta firmware of hexapod-firmware_c8875x_2.5.1.46.

```python
# set a trajectory for X
h.set_traj()

# run the trajectory
h.run_traj()

# get the records
dt = h.get_records()
# dt['X'] contains (target position, real position)

# plot the deviation
plot_record(dt, 'X')
```