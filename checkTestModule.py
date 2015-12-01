# ensure name sever is running with:
# python -m Pyro4.naming -n 10.2.5.32
# ensure the centralHub is running too
import Pyro4
ts=Pyro4.Proxy("PYRONAME:central.hub")
print ts.running()
