
class Singleton(type):
    def __new__(self, name, bases, dict):
        dict['_instances'] = {}
        return super().__new__(self, name, bases, dict)


    def __call__(base, *args, **kwargs):
        name = f"{base.__name__}__{hex(abs(hash(args)))}"
        try:
            cls_inst = base._instances[name]
        except KeyError:
            cls_inst = SingletonInstance(name, (base,), {})
            base._instances[name] = cls_inst
            cls_inst.init_once(*args)
        return cls_inst(**kwargs)
    


class SingletonInstance(Singleton):
    def __call__(self, *args, **kwargs): # override Singleton's __call__ to prevent recursion
        return super(Singleton, self).__call__(*args, **kwargs)

    def init_once(self, *args):
        pass
