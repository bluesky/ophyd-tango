# Experimental Ophyd–Tango Integration

## What is this?

Ophyd endeavors to provide a hardware abstraction that is control-layer
agonostic. So far this has been validated on:

* Channel Access (two different I/O libraries, pyepics and caproto)
* One-off socket protocols specific to particular hardwarwe
* Simualated hardware in Python

It has not yet been validated on a second fully-featured control layer such as
Tango. The goal of this project is to see what it would take to get ophyd
working with Tango, and to iron out any EPICS-specific assumptions that may have
leaked into ophyd's design despite the authors' best efforts.

## Prerequisites

This repo includes a ``docker-compose.yaml`` file obtained from the Tango
[documentaiton](https://tango-controls.readthedocs.io/en/latest/development/debugging-and-testing/testing-tango-using-docker.html).
You need ``docker-compose`` to run it. Install, e.g.


```sh
apt install docker-compose
```

or

```sh
brew install docker-compose
```

## Start Tango Test Database

```sh
git clone github.com/bluesky/ophyd-tango
cd ophyd-tango
docker-compose up --build
```

## Install client software

```sh
conda create -n pytango -c tango-controls python=3.7 pytango ipython
pip install ophyd  # I used pip to avoid conda-forge vs defaults conflicts.
```

## Overview of Design So Far

* ``TangoAttribute`` wraps a ``tango.AttributeProxy`` in the bluesky interface.
  An attribute has one value (could be an array) just like a PV does.
* ``TangoDevice`` wraps a ``tango.DeviceProxy``. Like ``ophyd.Device``, a
  ``TangoDevice`` has an internal structure. Unlike ``ophyd.Device``, the
  structure is encoded by the server and set up on the client at connection
  time, not encoded in the  class definition. So it seems there will just be
  *one* ``TangoDevice``, used directly, rather than many subclasses tuned to
  specific hardware. It will probably not use ``ophyd.Component`` internally;
  rather it will set up many ``AttributeProxy`` instances at ``__init__`` time.
* One could use ``ophyd.Device`` and ``ophyd.Component`` to build *larger* Devices
  out of ``TangoDevice`` and/or  ``TangoAttribute``.
* One could image convenience functions to query a tango database for all its
  devices and automatically build corresponding ``TangoDevice`` instances on
  demand.

## Run ophyd example

First, set this environment variable so that ``tango.Database()`` can find the
database running in Docker.

```sh
export TANGO_HOST=127.0.0.1:10000
```

Start IPython and run ``ophyd_tango.py`` in the user namespace. This perform
boilerplate bluesky setup and defines ``tango_attr``, an object that satisfies
a subset of the bluesky interface and connects to the ``double_scalar`` Tango
Attribute from the test database running in Docker.

```py
ipython -i ophyd_tango.py
```

Execute a simple bluesky plan like so:

```py
In [1]: RE(count([tango_attr], 10, 1), LiveTable(['double_scalar']))                                                                                                                          
+-----------+------------+---------------+
|   seq_num |       time | double_scalar |
+-----------+------------+---------------+
|         1 | 15:49:12.2 |      -204.450 |
|         2 | 15:49:13.2 |      -207.108 |
|         3 | 15:49:14.2 |      -207.108 |
|         4 | 15:49:15.2 |      -209.702 |
|         5 | 15:49:16.2 |      -209.702 |
|         6 | 15:49:17.2 |      -212.233 |
|         7 | 15:49:18.2 |      -212.233 |
|         8 | 15:49:19.2 |      -214.699 |
|         9 | 15:49:20.3 |      -214.699 |
|        10 | 15:49:21.3 |      -217.100 |
+-----------+------------+---------------+
generator count ['20a661f7'] (scan num: 1)
Out[1]: ('20a661f7-665c-412f-b4a0-78f69aaced52',)
```

## Notes

* Next step is to handle ``set()`` and ``subscribe()``. Tango's subscription
  semantics seem more sophisiticated than those in Channel Access. Ophyd's
  interface may need to be extended to fully utilize it.
* See ``first_steps.md`` for a log of some basic ``tango`` usage, including
  subscriptions.
