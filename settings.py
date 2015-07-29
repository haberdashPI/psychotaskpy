import expyriment as ex
import re
from multipledispatch import dispatch


class Default(object):
  pass


class Vars(object):
  def __init__(self,var_str):
    self.var_str = var_str


class UserRequest(object):
  def __init__(self):
    self.result = None


class UserNumber(UserRequest):
  def __init__(self,name,default,priority=float('inf')):
    UserRequest.__init__(self)
    self.name = name
    self.default = default
    self.priority = priority


class UserSelect(UserRequest):
  def __init__(self,name,options,results=None,priority=float('inf')):
    UserRequest.__init__(self)
    self.name = name
    self.options = options
    self.results = results
    self.priority = priority


class If(object):
  def __init__(self,condition_str,on_true,on_false=None):
    self.condition_str = condition_str
    self.on_true = on_true
    self.on_false = on_false


class Case(object):
  def __init__(self,key,cases):
    self.key = key
    self.cases = cases


class Plural(object):
  def __init__(self,name,default_item=None):
    self.name = name
    self.item = default_item


class Reference(object):
  def __init__(self,other_field):
    self.field = other_field


@dispatch(object)
def _stage_user_input(x):
  return {}


@dispatch(UserSelect)
def _stage_user_input(select):
  def fn(select=select):
    tm = ex.io.TextMenu(select.name,select.options,400)
    if select.results:
      key = select.options[tm.get(0)]
      x = select.results[key]
      x['name'] = key
      select.result = x
    else:
      select.result = select.options[tm.get(0)]

  return {select: (select.priority,fn)}


@dispatch(UserNumber)
def _stage_user_input(text):
  def fn(text=text):
    ti = ex.io.TextInput(text.name)
    text.result = int(ti.get(str(text.default)))

  return {text: (text.priority,fn)}


@dispatch((dict,list))
def _stage_user_input(values):
  requests = {}
  for key,item in _key_values(values):
    item_requests = _stage_user_input(item)

    for request_key,(priority,fn) in item_requests.iteritems():
      requests[request_key] = (priority,fn)

  return requests


@dispatch(object)
def _resolve_user_input(x):
  return x


@dispatch(UserRequest)
def _resolve_user_input(x):
  return x.result


@dispatch((dict,list))
def _resolve_user_input(values):
  for key,item in _key_values(values):
    values[key] = _resolve_user_input(item)
  return values


@dispatch(dict)
def _key_values(x):
  return x.iteritems()


@dispatch(list)
def _key_values(x):
  return enumerate(x)


# request_user_input makes all of the requests for user input for each user
# request object, doing so based on the priority of each user requests objects.
def request_user_input(settings):
  requests = _stage_user_input(settings).values()
  requests.sort(key=lambda x: x[0])
  for priority,request in requests:
    request()

  return _resolve_user_input(settings)

# resolve handles more complicated defaults that need
# to know about settings in the parent to work.
@dispatch(dict,object,object,dict)
def _resolve(result,key,default,parent):
  result[key] = default
  return result


@dispatch(dict,object,Plural,dict)
def _resolve(result,key,default,parent):
  if default.name in parent:
    result[key] = _merge(default,[parent[default.name]])
    del result[default.name]
    return result
  else:
    raise RuntimeError('Could not find singular or plural entry for "' +
                       default.name+'".')


@dispatch(object,object)
def _merge(default_a,a):
  return a


@dispatch(object,Default)
def _merge(default_a,a):
  return default_a


@dispatch(dict,dict)
def _merge(default,base):
    result = base.copy()
    for key,default_a in default.iteritems():
        if key in result: result[key] = _merge(default_a,result[key])
        else: result = _resolve(result,key,default_a,base)
    return result


@dispatch(Plural,list)
def _merge(default,base):
  return [_merge(default.item,b) for b in base]


class VariableResolver(dict):
  def __init__(self,settings,resolving):
    dict.__init__(self,settings)
    self.resolving = resolving
    self.settings = settings

  def __getitem__(self,key):
    if key in self.resolving:
      raise RuntimeError('Detected infinite loop!')
    else:
      return _replace_vars(dict.__getitem__(self,key),self.settings,
                           self.resolving & {key})


@dispatch(object,dict,set)
def _replace_vars(x,defined,resolving):
  return x


@dispatch(dict,dict,set)
def _replace_vars(child,top,resolving):
    for key,value in child.iteritems():
      child[key] = _replace_vars(value,_merge(child,top),resolving)
    return child


@dispatch(list,dict,set)
def _replace_vars(xs,defined,resolving):
  return [_replace_vars(x,defined,resolving) for x in xs]


@dispatch(Vars,dict,set)
def _replace_vars(vars,settings,resolving):
  braces = r'{([^}]+)}'
  result = vars.var_str
  try:
    for var in re.finditer(braces,vars.var_str):
      result = re.sub(braces,eval(var.group(1),globals(),
                                  VariableResolver(settings,resolving)),
                      result,1)
    return result
  except Exception as e:
    raise RuntimeError('Exception thrown while resolving "%s":\n%s' %
                       (vars.var_str,e))


@dispatch(If,dict,set)
def _replace_vars(ifobject,settings,resolving):
  try:
    result = eval(ifobject.condition_str,globals(),
                  VariableResolver(settings,resolving))
  except Exception as e:
    raise RuntimeError('Exception thrown while resolving "%s":\n%s' %
                       (ifobject.condition_str,e))

  if result: return _replace_vars(ifobject.on_true,settings,resolving)
  else: return _replace_vars(ifobject.on_false,settings,resolving)


@dispatch(Case,dict,set)
def _replace_vars(case,settings,resolving):
  values = VariableResolver(settings,resolving)
  return _replace_vars(case.cases[values[case.key]],settings,resolving)


@dispatch(str)
def key_summary(x):
  return x


@dispatch(tuple)
def key_summary(xs):
  return '_'.join(xs)


@dispatch(dict,object)
def summarize(settings,key):
  return settings[key]


@dispatch(dict,tuple)
def summarize(settings,key_tuple):
  value = settings
  for key in key_tuple:
    value = value[key]
  return value


@dispatch(dict,list)
def summarize(settings,keys):
  keysum = [key_summary(k) for k in keys]
  summary = dict(zip(keysum,[summarize(settings,k) for k in keys]))

  return keysum,summary


def prepare(settings,default={},final=False):
  settings = _merge(default,settings)
  if final: return _replace_vars(settings,settings,set())
  else: return settings
