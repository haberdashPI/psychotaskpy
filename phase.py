import inspect

_phases = {}

def phase(fn_or_name=None):
    def wrap(fn,name):
        if _phases.has_key(name):
            raise ValueError('Phase name "'+name+'" already in use.')
        if len(inspect.getargspec(fn).args) != 6:
            raise ValueError('A training phase function must have 6 arguments.')
        _phases[name] = fn
        return fn

    if callable(fn_or_name):
        return wrap(fn_or_name,fn_or_name.__name__)
    return lambda fn: wrap(fn,fn_or_name)

def list_phases():
    return _phases.keys()

def run_phase(str,*args):
    return _phases[str](*args)
