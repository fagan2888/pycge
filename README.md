# **pycge**: a Python package for CGE modeling #

This package provides an interface for solving a Computable
General Equilibrium (CGE) model in Python, using the package
[pyomo](www.pyomo.org) as the back end.

The aim of this package is to separate model *analysis* from model
*definition*. For a given a model definition, `pycge` provides a 
common interface for analysis, including: generating model instances
with different data sets; modifying model instances to simulate "shocks"; 
solving model instances; and post-processing solutions (e.g., conducting 
comparative statics).


## Requirements  

`python-3.x` and `pyomo 5.2`

## Setup and installation  

See `./docs/index.rst`

## Quick Start 

A quick summary of a standard workflow::

     # create model definition object
     testdef = ModelDef()

     # create pycge object
     testcge = PyCGE(testdef)
     
     # add data
     testcge.load_data(path/to/data)

     # create base instance
     testcge.model_instance()

     # calibrate base instance
     testcge.model_calibrate(solver, mgr='') 

     # create sim instance to modify
     testcge.model_sim() 

     # modify sim instance
     testcge.model_modify_instance(...) # modify some value
     testcge.model_modify_instnace(...) # modify another value
     
     # solve sim instance
     testcge.model_solve(solver, mgr='') 

     # compare base and sim equilibria
     testcge.model_compare()



## Credits  

The package is maintained by Juan Fung <[juan.fung@nist.gov](juan.fung@nist.gov)>

### Developers 

- [Charles Burtwistle](https://github.com/charleyburt)

