from types import IntType,StringType,FloatType,DictType,ListType,TupleType,ObjectType
import xn
from xn import Xn,inContext,firstLineOf

l1=firstLineOf

class Schema:
    def __init__(self,x):
        'initialse schema %(x)r'
        validateSchemaElement(x)
        self.x=x
        pass
    def __repr__(self):
        return repr(self.x)
    def validate(self,x):
        'verify that %(x)r conforms to jsonschema.Schema %(self)r'%vars()
        validate(self.x,x)
        return
    pass

def validateSchemaElement(x):
    'verify that %(x)r is a valid json schema element'
    try:
        if x is None: return
        if x in [IntType,StringType,FloatType]: return
        if type(x) is DictType:
            for name,y in x.items():
                try:
                    validateSchemaElement(y)
                except:
                    raise inContext('validate dict schema item %(name)r'%vars())
                pass
            return
        if type(x) is ListType:
            if not len(x) == 1:
                i=len(x)
                raise Xn('list schema must contain exactly one element, not %(i)s'%vars())
            validateSchemaElement(x[0])
            return
        if type(x) is TupleType:
            for i,y in enumerate(x):
                try:
                    validateSchemaElement(y)
                except:
                    raise inContext('validate tuple schema item %(i)r'%vars())
                pass
            return
        t=type(x)
        if t is ObjectType: t=x.__class__
        raise Xn('jsonschema element may not be a %(t)s, it must be a list, a dictionary or types.IntType, types.StringType, types.FloatType, types.TupleType or None'%vars())
    except:
        raise inContext(l1(validateSchemaElement.__doc__)%vars())
    pass


def validate(schema,x):
    'verify %(x)r conforms to json schema %(schema)r'
    try:
        if schema is None and not x is None:
            raise Xn('%(x)r is not None'%vars())
        if schema is IntType and not type(x) is IntType:
            raise Xn('%(x)r is not an Int'%vars())
        if schema is FloatType and not type(x) in [IntType,FloatType]:
            raise Xn('%(x)r is not a Float'%vars())
        if schema is StringType and not type(x) is StringType:
            raise Xn('%(x)r is not a String'%vars())
        if type(schema) is DictType:
            if not type(x) is DictType:
                raise Xn('%(x)r is not a Dictionary'%vars())
            for name, y in x.items():
                try:
                    if not name in schema:
                        keys=schema.keys()
                        raise Xn('%(name)r is not one of %(keys)r'%vars())
                    validate(schema[name],y)
                except:
                    raise inContext('validate dictionary item %(name)r'%vars())
                pass
            pass
        if type(schema) is ListType:
            if not type(x) is ListType:
                raise Xn('%(x)r is not a List'%vars())
            for i,y in enumerate(x):
                try:
                    validate(schema[0],y)
                except:
                    raise inContext('validate list item %(i)r'%vars())
                pass
            pass
        if type(schema) is TupleType:
            if len(schema) != len(x):
                sl=len(schema)
                xl=len(x)
                raise Xn('tuple has %(xl)s items not %(sl)s'%vars())
            for i,y in enumerate(x):
                try:
                    validate(schema[i],y)
                except:
                    raise inContext('validate tuple schema element %(i)s'%vars())
                pass
            pass
        pass
    except:
        raise inContext(l1(validate.__doc__)%vars())
    pass
                    

def test():
    Schema(IntType).validate(4)
    Schema(FloatType).validate(4)
    Schema(FloatType).validate(7.6)
    Schema(StringType).validate('fred')
    Schema([IntType]).validate([])
    Schema([IntType]).validate([5,6])
    Schema({'a':IntType,'b':StringType}).validate({'a':8,'b':'fred'})
    Schema([{'a':IntType,'b':StringType}]).validate([{'a':8,'b':'fred'},{'a':7,'b':'jock'}])
    Schema((IntType,StringType)).validate([8,'fred'])
    try:
        Schema(IntType).validate('fred')
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify 'fred' conforms to json schema <type 'int'> because\n'fred' is not an Int.",repr(str(e))
    try:
        Schema(FloatType).validate('fred')
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify 'fred' conforms to json schema <type 'float'> because\n'fred' is not a Float.",repr(str(e))
    try:
        Schema(StringType).validate(4)
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify 4 conforms to json schema <type 'str'> because\n4 is not a String.",repr(str(e))
    try:
        Schema([StringType]).validate([4])
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify [4] conforms to json schema [<type 'str'>] because\nfailed to validate list item 0 because\nfailed to verify 4 conforms to json schema <type 'str'> because\n4 is not a String.",repr(str(e))
    try:
        Schema([StringType]).validate(['fred',4])
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify ['fred', 4] conforms to json schema [<type 'str'>] because\nfailed to validate list item 1 because\nfailed to verify 4 conforms to json schema <type 'str'> because\n4 is not a String.",repr(str(e))
    try:
        Schema({'a':IntType,'b':StringType}).validate({'a':8,'b':6})
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify {'a': 8, 'b': 6} conforms to json schema {'a': <type 'int'>, 'b': <type 'str'>} because\nfailed to validate dictionary item 'b' because\nfailed to verify 6 conforms to json schema <type 'str'> because\n6 is not a String.",repr(str(e))
        pass
    
if __name__=='__main__':
    test()
