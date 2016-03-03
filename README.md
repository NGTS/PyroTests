# CentralHub

This process monitors external NGTS processes through `Pyro4`.

The way the class monitors status is a series of boolean values
representing ok or not, and a corresponding set of integers. When a
process checks in, the integer value of the check state is set to
`_ntimes` (e.g. 5) and then every time the status poll loop checks the
state, it decrements this counter. If the counter is 0 then the `status`
value is set to `False`.

## Usage

In the external process code, add the following shippet:

```python
import Pyro4

hub = Pyro4.Proxy('PYRONAME:central.hub')
```

and then in the polling loop add the following:

```python
hub.report_in('<name>')
```

where `name` is the name of the process type (case insensitive).
For example with the transparency code:

```python
hub.report_in('transparency')
```

The variables `_ntimes` and `_sleeptime` control the timeouts for each
monitored process. If a process has not reported in for `_ntimes` loops
of `_sleeptime` seconds, the status is set to `False`.

## Return values

To check if everything updated ok, `report_in` returns a list of status
dictionaries. For example a successful update may look like:

```python
[{'name': 'transparency',
    'previous': {'connections': 0, 'status': False},
    'ok': True}]
```

A failure (for example using an incorrect name) may look like this:

```python
[{'reason': "No monitor for lkjnasg. Available monitors: ['alcor',
    'cloud_watcher', 'microphones', 'rain_sensor', 'transparency']",
    'ok': False}]
```

## Possible errors

If there are connection issues, this will result in `report_in` hanging
and blocking the calling code. `Pyro4` will raise a timeout exception
which is worth catching and handling properly. *Note this will not occur
when creating the `Pyro4.Proxy` object, but rather when calling a method
on this object.*
