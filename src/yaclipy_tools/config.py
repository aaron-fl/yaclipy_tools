


class ConfigVar():
    UNSET = object()
    
    def __init__(self, doc, default):
        self.doc = doc
        self.default = default
        self.value = ConfigVar.UNSET
    

    def __call__(self, value=UNSET):
        if value != ConfigVar.UNSET: self.value = value
        return self.default if self.value == ConfigVar.UNSET else self.value 



class Config():
    @staticmethod
    def var(*args, **kwargs):
        return ConfigVar(*args, **kwargs)
