# ensure name sever is running with:
# python -m Pyro4.naming -n 10.2.5.32
import Pyro4
ts=Pyro4.Proxy("PYRONAME:example.test")
print ts.running()
