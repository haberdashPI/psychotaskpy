import expyriment as ex
import re
from multipledispatch import dispatch


class Default(object):
  pass


class Vars(object):
  def __init__(self,var_str):
    self.var_str = var_str


class UserNumber(object):
  def __init__(self,name,default,priority=float('inf')):
    self.name = name
    self.default = default
    self.priority = priority


class UserSelect(object):
  def __init__(self,name,options,results=None,priority=float('inf')):
    self.name = name
    self.options = options
    self.results = results
    self.priority = priority

# _request_user_input takes an object x to request input for and returns a list
# of requests. A request consists of a priority and a function. THe priority
# determiens the order requests are made to the user, and the function actually
# makes the request of a user, taking as input object x, and returning the
# modified value of object x after the particular request for user input.
@dispatch(object)
def _request_user_input(x):
  return []


@dispatch(UserSelect)
def _request_user_input(select):
  def fn(select):
    tm = ex.io.TextMenu(select.name,select.options,400)
    if select.results:
      key = select.options[tm.get(0)]
      x = select.results[key]
      x['key'] = key
      return x
    else: return select.options[tm.get(0)]

  return [(select.priority,fn)]


@dispatch(UserNumber)
def _request_user_input(text):
  def fn(text):
    ti = ex.io.TextInput(text.name)
    return int(ti.get(str(text.default)))

  return [(text.priority,fn)]


@dispatch(dict)
def _request_user_input(settings):
  requests = []
  for key,item in settings.iteritems():
    item_requests = _request_user_input(item)

    for priority,request in item_requests:
      def fn(settings,key=key,item=item,request=request):
        print "Requesting ",key
        settings[key] = request(item)
        return settings
      requests.append((priority,fn))

  return requests


# request_user_input makes all of the requests for user input to modify a set
# of objects, doing so in the order of priority from lowest to highest.
def request_user_input(settings):
  requests = _request_user_input(settings)
  requests.sort(key=lambda x: x[0])
  for priority,request in requests:
    settings = request(settings)

  return settings


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
        else: result[key] = default_a
    return result


@dispatch(object,dict)
def _replace_vars(x,defined):
  return x


@dispatch(dict,dict)
def _replace_vars(child,top):
    for key,value in child.iteritems():
      child[key] = _replace_vars(value,top)
    return child


@dispatch(list,dict)
def _replace_vars(xs,defined):
  return map(lambda x: _replace_vars(x,defined), xs)


@dispatch(Vars,dict)
def _replace_vars(vars,settings):
  braces = r'{([^}]+)}'
  result = vars.var_str
  try:
    for var in re.finditer(braces,vars.var_str):
      result = re.sub(braces,eval(var.group(1),globals(),settings),result,1)
    return result
  except Exception as e:
    raise RuntimeError('Exception thrown while resolving %s:\n%s' %
                       vars.var_str,e)

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
  if final: return _replace_vars(settings,settings)
  else: return settings
