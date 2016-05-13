from sider import types
from limpyd import fields


# These types all extend types.Bulk
# https://sider.readthedocs.io/en/0.3.1/sider/types.html
from limpyd.utils import incr_list

BULK_TYPES = [
    types.TimeDelta,
    types.UUID,
    types.UnicodeString,
    types.TZDateTime,
    types.Time,
    types.Integer,
    # types.Tuple,  - container / composite type, need special support
    types.TZTime,
    types.String,
    types.Date,
    # types.SortedSet,  - container / composite type, need special support
    types.DateTime,
    types.Boolean,
    types.ByteString,
]


RAW_VALUE_PARAMS = {
    "setbit": [2],
    "setrange": [2]
}

# Map of command parameters that can be values
TYPEABLE_VALUE_PARAMS = {
    "append": [1],
    "linsert": [-1],  # http://redis.io/commands/linsert
    "lpush": [1, ...],
    "lpushx": [1],
    "lrem": [2],
    "lset": [2],
    "mget": [1],
    "mset": incr_list([1], 2),
    "msetnx": incr_list([1], 2),
    "psetnx": [2],
    "rpush": incr_list([1]),
    "set": [1],
    "setex": [2],
    "setnx": [1],
}

def wrap_getter(func):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        return self.to_python(result)
    return wrapper

def modify_args(args, argspec):
    pass

def wrap_modifier(func, command_name):
    def wrapper(self, *args, **kwargs):
        print("wrap_modifier")
        argspec = TYPEABLE_VALUE_PARAMS[command_name]
        modifier_args = args
        result = func(self, *modifier_args, **kwargs)
        return result
    return wrapper

class SiderField(fields.StringField):
    """
    Use Sider.types to encode and decode data
    """
    available_getters = ("get",)
    available_modifiers = ("set",)

    @classmethod
    def _make_command_method(cls, command_name):
        is_getter = command_name in cls.available_getters
        is_modifier = command_name in cls.available_modifiers
        is_both = is_getter and is_modifier

        def func(self, *args, **kwargs):
            result = self._call_command(command_name, *args, **kwargs)
            return result

        if is_both:
            print("wrapping both is unsupported")
            return func
        elif is_getter:
            return wrap_getter(func)
        elif is_modifier:
            return wrap_modifier(func, command_name)
        else:
            return func

def create_bulk_field_t(sider_ti):
    """
    :param   sider_t: sider type (should extend types.Bulk)
    :return: new field class
    """
    def to_python(self, value):
        if value is None:
            # Possibly should raise KeyError ?
            return None
        result = sider_ti.decode(value)
        return result

    def to_storage(self, value):
        result = sider_ti.encode(value)
        return result

    sider_t = sider_ti.__class__
    name = "%sField" % sider_t.__name__
    dct = dict(
        to_python = to_python,
        to_storage = to_storage,
        override_make_command = True,
    )
    klass = type(name, (SiderField,), dct)
    return klass


def create_bulk_field_types():
    """
    Create all the bulk types, e.g. IntegerField
    """
    for sider_t in BULK_TYPES:
        type_inst = sider_t()
        klass = create_bulk_field_t(type_inst)
        yield klass.__name__, klass

globals().update(**dict(create_bulk_field_types()))