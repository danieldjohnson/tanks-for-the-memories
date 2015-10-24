from SimpleObjectPolicies import Containers, ContainerAssertions

class SecurityManager(object):
    # def validate(self, *args):
    def validate(self, accessed=None, container=None, name=None, value=None,
             *args):
        # print "Validate:", (accessed,container,name,value,args)
        p = Containers(type(container), None)
        if p is None:
            p = getattr(container,
                        '__allow_access_to_unprotected_subobjects__',
                        None)

        if p is None:
            print "wrapget", container
            p = getattr(container,
                        '__guarded_getattr_validate__',
                        None)

        if p is not None:
            if not isinstance(p, int): # catches bool too
                if isinstance(p, dict):
                    if isinstance(name, basestring):
                        p = p.get(name)
                    else:
                        p = 1
                else:
                    p = p(name, value)

        if p:
            return 1
        else:
            raise Unauthorized

sm = SecurityManager()

def getSecurityManager():
    return sm

def secureModule(mname, globals, locals):
    if mname in ['math', 'random', 'functools', 'itertools', 'copy']:
        return __import__(mname, globals, locals)
    return None

class Unauthorized(Exception):
    pass

_marker = object()

def guarded_getattr(inst, name, default=_marker):
    """Retrieves an attribute, checking security in the process.
    Raises Unauthorized if the attribute is found but the user is
    not allowed to access the attribute.
    """
    if name[:1] == '_':
        raise Unauthorized, name

    # Try to get the attribute normally so that unusual
    # exceptions are caught early.
    try:
        v = getattr(inst, name)
    except AttributeError:
        if default is not _marker:
            return default
        raise

    getSecurityManager().validate(inst, inst, name, v)
    
    return v