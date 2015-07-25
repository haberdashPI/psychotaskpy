import inspect

_phases = {}
_phase_defaults = {}

def phase(fn_or_name=None):
    def wrap(fn,name):
        if name in _phases:
            raise ValueError('Phase name "'+name+'" already in use.')
        if len(inspect.getargspec(fn).args) != 3:
            raise ValueError('A training phase function must take 3 arguments.')
        _phases[name] = fn
        return fn

    if callable(fn_or_name):
        return wrap(fn_or_name,fn_or_name.__name__)
    return lambda fn: wrap(fn,fn_or_name)


def phase_defaults(name=None):
    def wrap(fn,name):
        if name not in _phases:
            raise ValueError('Phase name "'+name+'" does not exist.')
        if len(inspect.getargspec(fn).args) != 1:
            raise ValueError('A training phase defaults function must take 1 argument')
        _phase_defaults[name] = fn
        return fn

    return lambda fn: wrap(fn,name)

def list_phases():
    return _phases.keys()


def run_phase(str,*args):
    return _phases[str](*args)
def get_phase_defaults(env):
    if env['phase'] in _phase_defaults:
        return _phase_defaults[env['phase']](env)
    else:
        return lambda env: {}
