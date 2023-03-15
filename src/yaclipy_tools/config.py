import traceback, os, copy, inspect, re
from .singleton import Singleton
from print_ext import Table, Text, PrettyException, pretty


class InvalidTarget(PrettyException):
    def pretty(self, **kwargs):
        p = Printer()
        p(f'\berr {self.target}\b  is not a valid target.  Valid targets are:')
        for t in Config.valid_targets():
            p(f' * \b1 {t}')
        return p



class ConfigTargetUnset(PrettyException):
    def pretty(self, **kwargs):
        return Text(f"You cannot access config variables until \b1 Config.set_target()\b  has been called.")



class ConfigVar():
    UNSET = object()
    NAME = re.compile(r'\s*(\w+)\s*=')
    
    def __init__(self, doc, default, coerce=lambda x:x):
        self.dfns = []
        self.doc = doc
        self.coerce = coerce
        self.default = default
        self.value = ConfigVar.UNSET
        self._value = ConfigVar.UNSET
        tb = traceback.extract_stack(limit=3)[0]
        name = ConfigVar.NAME.match(tb.line)
        name = name[1] if name else 'undefined'
        self.name = name if tb.name.startswith('<') else f"{tb.name}.{name}"
        self.dfns = [(os.path.relpath(tb.filename), tb.lineno)]


    def reset(self):
        self.set(copy.deepcopy(self.default))
        self.dfns[1:] = []
        

    def set(self, value, offset=0):
        self.value = value
        self._value = ConfigVar.UNSET
        tb = traceback.extract_stack(limit=3+offset)[0]
        self.dfns.append((os.path.relpath(tb.filename), tb.lineno))


    def __call__(self, value=UNSET):
        if self._value == ConfigVar.UNSET and self.value != ConfigVar.UNSET:
            self._value = self.coerce(self.value() if inspect.isroutine(self.value) else self.value)
        if value != ConfigVar.UNSET:
            self.set(value)
        elif self._value == ConfigVar.UNSET:
            raise ConfigTargetUnset()
        return self._value
       


class ConfigTarget():

    def override(self, name=None, before=None, after=None, mutex=None, implicit=None): 
        def _override(fn):
            fn_orig = self.fn
            def _chainup():
                fn_orig()
                fn()
            self.fn = _chainup
            self.set_name(name or fn.__name__)
            if before != None: self.set_group('before', before)
            if after != None: self.set_group('after', after)
            if mutex != None: self.set_group('mutex', mutex)
            if implicit != None: self.implicit = implicit
        return _override


    def __init__(self, fn, name=None, before=[], after=[], mutex=[], implicit=False):
        self.fn = fn
        self.name = None
        self.implicit = implicit
        self.set_name(name or fn.__name__)
        self.set_group('before', before)
        self.set_group('after', after)
        self.set_group('mutex', mutex)


    def set_group(self, attr, val):
        if isinstance(val, str): val = val.split(' ')
        setattr(self, attr, set([n.lower() for n in val]))


    def set_name(self, name):
        name = name.replace('_','-')
        Config.retarget(self.name, name, self)
        self.name = name


    def __hash__(self):
        return hash(self.name.lower())


    def __eq__(self, other):
        return self.name.lower() == str(other).lower()


    def __repr__(self):
        return self.name




class Config():
    vars = []
    targets = {}
    _valid_targets = None
    cur_target = ''

    @classmethod
    def retarget(self, name_old, name_new, target):
        if name_old != None and name_old.lower() != name_new.lower():
            del self.targets[name_old.lower()]
        self.targets[name_new.lower()] = target
        self._valid_targets = None


    @classmethod
    def set_target(self, target):
        if self.cur_target.lower() == target.lower(): return
        for v in self.vars: v.reset()
        if target == '-': return
        if not self.is_valid_target(target):
            raise InvalidTarget(target=target)
        targets = target.split('.')
        for t in self.targets.values():
            if not t.implicit: continue
            targets.insert(0, t.name)
        for t in targets:
            self.targets[t.lower()].fn()
        self.cur_target = target


    @classmethod
    def var(self, *args, **kwargs):
        var = ConfigVar(*args, **kwargs)
        self.vars.append(var)
        return var


    @classmethod
    def target(self, **kwargs):
        def _f(fn):
            return ConfigTarget(fn, **kwargs)
        return _f


    @classmethod
    def valid_targets(self):
        if self._valid_targets != None: return self._valid_targets
        self._valid_targets = set()
        def _after_fail(t, target):
            if not t.after: return
            for a in t.after:
                if a in target: return
            return True
        def _mutex_fail(t, target):
            for m in t.mutex:
                if m in target: return True
        def _try(target):
            for t in self.targets.values():
                if t in target or t.implicit: continue
                if _after_fail(t,target): continue
                if _mutex_fail(t,target): continue
                target.append(t)
                if not t.before: self._valid_targets.add('.'.join(t.name for t in target))
                _try(target)
                target.pop()
        _try([])
        return self._valid_targets
        

    @classmethod
    def is_valid_target(self, target):
        for t in self.valid_targets():
            if t.lower() == target.lower(): return True


    @classmethod
    def pretty(self, **kwargs):
        p = Printer()
        tbl = Table(1,1,100, tmpl='pad')
        tbl.cell('C0', style='1', just='>')
        for var in self.vars:
            tbl(var.name,'\t', pretty(var()),'\t',var.doc,'\t')
        p(tbl, pad=1)
        p.hr('Targets', pad=1)
        for name in self.valid_targets():
            p(' * ', '\b1$', name)
        return p
        