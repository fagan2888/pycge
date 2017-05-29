# Pyomo port of splcge.gms from GAMS Model Library


# ------------------------------------------- #
# Import packages
from pyomo.environ import *
import pandas as pd
import numpy as np


# ------------------------------------------- #
# MODEL OBJECT: "Container for problem"
# Create abstract model
model = AbstractModel()


# ------------------------------------------- #
# DEFINE SETS
model.i = Set(doc='goods')
model.h = Set(doc='factor')
model.u = Set(doc='SAM entry')


# ------------------------------------------- #
# Unnecessary: in GAMS, aliases
# model.j = SetOf(model.i)
# model.k = SetOf(model.h)
# model.v = SetOf(model.u)


# ------------------------------------------- #
# DEFINE PARAMETERS
model.sam = Param(model.u, model.u, doc='social accounting matrix')


def X0_init(model, i):
    return model.sam[i, 'HOH']


model.X0 = Param(model.i, initialize=X0_init,
                 doc='household consumption of the i-th good')


def F0_init(model, h, i):
    return model.sam[h, i]


model.F0 = Param(model.h, model.i, initialize=F0_init,
                 doc='the h-th factor input by the j-th firm')


def Z0_init(model, i):
    return sum(model.F0[h, i] for h in model.h)


model.Z0 = Param(model.i, initialize=Z0_init, doc='output of the j-th good')


def FF_init(model, h):
    return model.sam['HOH', h]


model.FF = Param(model.h, initialize=FF_init,
                 doc='factor endowment of the h-th factor')


# ------------------------------------------- #
# CALIBRATION


def alpha_init(model, i):
    return model.X0[i] / sum(model.X0[j] for j in model.i)

model.alpha = Param(model.i, initialize=alpha_init,
                    doc='share parameter in utility function')


def beta_init(model, h, i):
    return model.F0[h, i] / sum(model.F0[k, i] for k in model.h)

model.beta = Param(model.h, model.i, initialize=beta_init,
                   doc='share parameter in production function')


def b_init(model, i):
    return model.Z0[i] / np.prod([model.F0[h, i]**model.beta[h, i] for h in model.h])

model.b = Param(model.i, initialize=b_init,
                doc='scale paramater in production function')


# ------------------------------------------- #
# Define model system
# DEFINE VARIABLES

model.X = Var(model.i,
              initialize=X0_init,
              within=PositiveReals,
              doc='household consumption of the i-th good')

# def F_init(model, h, j):

model.F = Var(model.h, model.i,
              initialize=F0_init,
              within=PositiveReals,
              doc='the h-th factor input by the j-th firm')

model.Z = Var(model.i,
              initialize=Z0_init,
              within=PositiveReals,
              doc='output of the j-th good')


def p_init(model, v):
    return 1

model.px = Var(model.i,
               initialize=p_init,
               within=PositiveReals,
               doc='demand price of the i-th good')

model.pz = Var(model.i,
               initialize=p_init,
               within=PositiveReals,
               doc='supply price of the i-th good')

model.pf = Var(model.h,
               initialize=p_init,
               within=PositiveReals,
               #bounds = pf_fix,
               doc='the h-th factor price')


# Unnecessary: in gams, stores objective function *value*
# model.UU = Var(doc='utility [fictitious]')


# ------------------------------------------- #
# DEFINE EQUATIONS
# define constraints
def eqX_rule(model, i):
    return (model.X[i] == model.alpha[i] * sum(model.pf[h] * model.FF[h] / model.px[i] for h in model.h))

model.eqX = Constraint(model.i, rule=eqX_rule, doc='household demand function')


def eqpz_rule(model, i):
    return (model.Z[i] == model.b[i] * np.prod([model.F[h, i]**model.beta[h, i] for h in model.h]))

model.eqpz = Constraint(model.i, rule=eqpz_rule, doc='production function')


def eqF_rule(model, h, i):
    return (model.F[h, i] == model.beta[h, i] * model.pz[i] * model.Z[i] / model.pf[h])

model.eqF = Constraint(model.h, model.i, rule=eqF_rule,
                       doc='factor demand function')


def eqpx_rule(model, i):
    return (model.X[i] == model.Z[i])

model.eqpx = Constraint(model.i, rule=eqpx_rule,
                        doc='good market clearning condition')


def eqpf_rule(model, h):
    return (sum(model.F[h, j] for j in model.i) == model.FF[h])

model.eqpf = Constraint(model.h, rule=eqpf_rule,
                        doc='factor market clearning condition')


def eqZ_rule(model, i):
    return (model.px[i] == model.pz[i])

model.eqZ = Constraint(model.i, rule=eqZ_rule, doc='price equation')


# ------------------------------------------- #
# DEFINE OBJECTIVE
def obj_rule(model):
    return np.prod([model.X[i]**model.alpha[i] for i in model.i])

model.obj = Objective(rule=obj_rule, sense=maximize,
                      doc='utility function [fictitious]')


# ------------------------------------------- #
# CREATE MODEL INSTANCE

data = DataPortal()
data.load(filename='./splcge-set-i.csv', format='set', set='i')
data.load(filename='./splcge-set-h.csv', format='set', set='h')
data.load(filename='./splcge-set-u.csv', format='set', set='u')
data.load(filename='./splcge-sam.csv', param='sam', format='array')

instance = model.create_instance(data)
instance.pf['LAB'].fixed = True
instance.pprint()


# ------------------------------------------- #
# SOLVE
# Using NEOS external solver

# Select solver
solver = 'minos'  # 'ipopt', 'knitro', 'minos'
solver_io = 'nl'

# Solve and write results to stdout
# NB: for scripting in python interpreter
# with SolverManagerFactory("neos") as solver_mgr:
#    results = solver_mgr.solve(instance, opt=solver)
#    results.write()


# ------------------------------------------- #
# Display results
def pyomo_postprocess(options=None, instance=None, results=None):
    instance.X.display()
    instance.px.display()
    instance.Z.display()
    instance.obj.display()


# pyomo_postprocess(instance=instance)


# ------------------------------------------- #
# To run as python script:

# This is an optional code path that allows the script to be run outside of
# pyomo command-line.  For example:  python splcge_demo.py
if __name__ == '__main__':
    #This replicates what the pyomo command-line tools does
    from pyomo.opt import SolverFactory
    import pyomo.environ
    #opt = SolverFactory(solver)
    #opt.options['max_iter'] = 20
    with SolverManagerFactory("neos") as solver_mgr:
        results = solver_mgr.solve(instance, opt=solver, tee=True)
        results.write()
    pyomo_postprocess(instance=instance)

# ------------------------------------------- #
# TODO:
# 1. loading csv, etc.
#    - using DataPortal()
#    - using pandas, etc.
# 2. displaying output, exporting results
# 3. functions/classes: model creation separate from
#    model solution (ie, model instance with data import)
# 4. warap in module(s) -> package?
# 5. unit testing
