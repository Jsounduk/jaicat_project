_REGISTRY = {}

def command(name):
    def wrap(fn):
        _REGISTRY[name] = fn
        return fn
    return wrap

def get_registry():
    return dict(_REGISTRY)
