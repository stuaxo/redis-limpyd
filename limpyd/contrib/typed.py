from sider import types
from limpyd import fields


# These types all extend types.Bulk
# https://sider.readthedocs.io/en/0.3.1/sider/types.html
BULK_TYPES = [
    types.TimeDelta,
    types.UUID,
    types.UnicodeString,
    types.TZDateTime,
    types.Time,
    types.Integer,
    types.Tuple,
    types.TZTime,
    types.String,
    types.Date,
    types.SortedSet,
    types.DateTime,
    types.Boolean,
    # types.ByteString,
]

# VALUE_TYPES = [ types.Bulk, types.Hash, types.List, types.Set, ]

def create_bulk_field_t(sider_t):
    """
    :param   sider_t: sider type (should extend types.Bulk)
    :return: new field class
    """
    class SiderField(fields.StringField):
        t_inst = sider_t()

        available_getters = ["get"]
        available_modifiers = ["set"]
        def to_python(value):
            if value is not None:
                t = SiderField.t_inst
                result = t.encode(value)
                print("encoded: ", type(result), result)
                return result

        def to_storage(value):
            print("to_storage: ", value)
            return value

    SiderField.__name__ = "%sField" % sider_t.__name__
    return SiderField

def create_bulk_field_types():
    """
    Create all the bulk types, e.g. IntegerField
    """
    for sider_t in BULK_TYPES:
        klass = create_bulk_field_t(sider_t)
        yield klass.__name__, klass


globals().update(**dict(create_bulk_field_types()))