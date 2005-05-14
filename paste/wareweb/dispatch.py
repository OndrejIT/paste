from paste import httpexceptions
import event

__all__ = ['public', 'ActionDispatch', 'PathDispatch']

def public(func):
    func.public = True
    return func

class MethodDispatch(object):

    prefix = None

    def __addtoclass__(self, attr, cls):
        cls.listeners.append(self.respond_event)
    
    def respond_event(self, name, servlet, *args, **kw):
        if name == 'end_awake':
            return self.find_method(servlet, *args, **kw)
        return event.Continue

    def get_method(self, servlet, action):
        try:
            return action, getattr(servlet, action)
        except AttributeError:
            pass
        if self.prefix:
            try:
                return (self.prefix + action,
                        getattr(servlet, self.prefix + action))
            except AttributeError:
                pass
        return None, None

    def valid_method(self, name, method):
        if getattr(method, 'public', False):
            return True
        if self.prefix and name.startswith(self.prefix):
            return True
        return False
    
class ActionDispatch(MethodDispatch):

    prefix = 'action_'

    def __init__(self, action_name='_action_'):
        self.action_name = action_name

    def find_method(self, servlet, ret_value):
        possible_actions = []
        for name, value in servlet.fields.items():
            if name == self.action_name:
                possible_actions.append(value)
            elif name.startswith(self.action_name):
                possible_actions.append(name[len(self.action_name):])
        if not possible_actions:
            return event.Continue
        if len(possible_actions) > 1:
            raise httpexceptions.HTTPBadRequest(
                "More than one action received: %s"
                % ', '.join(map(repr, possible_actions)))
        action = possible_actions[0]
        name, method = self.get_method(servlet, action)
        if name is None:
            raise httpexceptions.Forbidden(
                "Action method not found: %r" % action)
        if not self.valid_method(name, method):
            raise httpexceptions.Forbidden(
                "Method not allowed: %r" % action)
        return method()

class PathDispatch(MethodDispatch):

    prefix = 'path_'

    def find_method(self, servlet, ret_value):
        parts = servlet.path_parts
        if not parts:
            action == 'index'
        else:
            action == parts[0]
            servlet.path_parts = parts[1:]
        name, method = self.get_method(servlet, action)
        if name is None:
            raise httpexceptions.Forbidden(
                "Method not found: %r" % action)
        if not self.valid_method(name, method):
            raise httpexceptions.Forbidden(
                "Method not allowed: %r" % action)
        return method()
    
