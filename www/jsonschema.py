from types import IntType,StringType,UnicodeType,FloatType,DictType,ListType,TupleType,ObjectType,BooleanType
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
        return validate(self.x,x)
        return
    pass

class OneOf:
    def __init__(self,*choices):
        self.choices=choices
        pass
    def __str__(self):
        return 'one of %(choices)s'%self.__dict__
    def __repr__(self):
        return 'one of %(choices)r'%self.__dict__
    pass

def validateSchemaElement(x):
    'verify that %(x)r is a valid json schema element'
    try:
        if x is None: return
        if x in [IntType,StringType,FloatType,BooleanType]: return
        if type(x) in [IntType,StringType,UnicodeType]: return #literal
        if type(x) is DictType:
            if len(x) == 1 and x.keys()[0] in (IntType,StringType):
                validateSchemaElement(x.values()[0])
                return
            for name,y in x.items():
                try:
                    assert type(name) is StringType, type(name)
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
        if isinstance(x,OneOf):
            for c in x.choices:
                validateSchemaElement(c)
                pass
            return
        if isinstance(x,Schema):
            return
        t=type(x)
        if t is ObjectType: t=x.__class__
        raise Xn('jsonschema element may not be a %(t)s, it must be a list, a dictionary or types.IntType, types.StringType, types.UnicodeType, types.FloatType, types.BooleanType, types.TupleType or None'%vars())
    except:
        raise inContext(l1(validateSchemaElement.__doc__)%vars())
    pass

def validate(schema,x):
    'verify %(x)r conforms to json schema %(schema)r'
    try:
        if schema is None and not x is None:
            raise Xn('%(x)r is not None'%vars())
        if type(schema) is IntType:
            if not type(x) is IntType:
                raise Xn('%(x)r is not an integer'%vars())
            if not x==schema:
                raise Xn('%(x)r is not %(schema)r'%vars())
            pass
        if type(schema) in [UnicodeType,StringType]:
            if not type(x) in [StringType,UnicodeType]:
                raise Xn('%(x)r is not a string'%vars())
            if not x==schema:
                raise Xn('%(x)r is not %(schema)r'%vars())
            pass
        if schema is IntType and not type(x) is IntType:
            raise Xn('%(x)r is not an Int'%vars())
        if schema is BooleanType and not type(x) is BooleanType:
            raise Xn('%(x)r is not an Int'%vars())
        if schema is FloatType and not type(x) in [IntType,FloatType]:
            raise Xn('%(x)r is not a Float'%vars())
        if schema is StringType and not type(x) in [StringType,UnicodeType]:
            raise Xn('%(x)r is not a String'%vars())
        if type(schema) is DictType:
            if not type(x) is DictType:
                raise Xn('%(x)r is not a Dictionary'%vars())
            if len(schema)==1 and schema.keys()[0] in (IntType,StringType):
                for key,y in x.items():
                    try:
                        validate(schema.keys()[0],key)
                        validate(schema.values()[0],y)
                    except:
                        raise inContext('validate dictionary item %(key)r'%vars())
                    pass
                return x
            for name, y in x.items():
                try:
                    if not name in schema:
                        keys=schema.keys()
                        raise Xn('%(name)r is not one of %(keys)r'%vars())
                    validate(schema[name],y)
                except:
                    raise inContext('validate dictionary item %(name)r'%vars())
                pass
            for name in schema:
                if not name in x:
                    raise Xn('%(name)r is missing'%vars())
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
        if isinstance(schema,OneOf):
            choices=schema.choices[:]
            failures=[]
            while len(choices):
                try:
                    validate(choices[0],x)
                    return x
                except Exception,e:
                    failures.append(e)
                    pass
                choices=choices[1:]
                pass
            raise Xn(' and '.join([str(_) for _ in failures]))
        if isinstance(schema,Schema):
            schema.validate(x)
            pass
        return x
    except:
        raise inContext(l1(validate.__doc__)%vars())
    pass
                    

def test():
    Schema(None).validate(None)
    Schema(2).validate(2)
    Schema('fred').validate('fred')
    Schema(IntType).validate(4)
    Schema(BooleanType).validate(True)
    Schema(FloatType).validate(4)
    Schema(FloatType).validate(7.6)
    Schema(StringType).validate('fred')
    Schema(StringType).validate(u'fred')
    Schema([IntType]).validate([])
    Schema([IntType]).validate([5,6])
    Schema({'a':IntType,'b':StringType}).validate({'a':8,'b':'fred'})
    Schema([{'a':IntType,'b':StringType}]).validate([{'a':8,'b':'fred'},{'a':7,'b':'jock'}])
    Schema((IntType,StringType)).validate([8,'fred'])
    Schema({IntType:StringType}).validate({1:'fred',2:'jock'})
    Schema({StringType:IntType}).validate({'fred':1,'jock':2})
    Schema({StringType:IntType}).validate({u'fred':1,'jock':2})
    Schema(OneOf(IntType,StringType)).validate(1)
    Schema(OneOf(IntType,StringType)).validate('fred')
    Schema([Schema(IntType)]).validate([1,2,3])
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
    try:
        Schema({IntType:StringType}).validate({'sal':'fred',2:'jock'})
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify {2: 'jock', 'sal': 'fred'} conforms to json schema {<type 'int'>: <type 'str'>} because\nfailed to validate dictionary item 'sal' because\nfailed to verify 'sal' conforms to json schema <type 'int'> because\n'sal' is not an Int.",repr(str(e))
        pass
    try:
        Schema(OneOf(IntType,StringType)).validate(None)
        assert None
    except Exception,e:
        assert str(e)=="Failed to verify None conforms to json schema one of (<type 'int'>, <type 'str'>) because\nFailed to verify None conforms to json schema <type 'int'> because\nNone is not an Int. and Failed to verify None conforms to json schema <type 'str'> because\nNone is not a String..",repr(str(e))
        
        pass
    try:
        Schema(None).validate(True)
        assert None
    except Exception,e:
        assert str(e)=='Failed to verify True conforms to json schema None because\nTrue is not None.',repr(str(e))
        pass
    try:
        Schema(2).validate(3)
        assert None
    except Exception,e:
        assert str(e)=='Failed to verify 3 conforms to json schema 2 because\n3 is not 2.',repr(str(e))
        pass
    try:
        Schema(2).validate('jock')
        assert None
    except Exception,e:
        assert str(e)=='''Failed to verify 'jock' conforms to json schema 2 because\n'jock' is not an integer.''',repr(str(e))
        pass
    try:
        Schema('fred').validate(1)
        assert None
    except Exception,e:
        assert str(e)=='''Failed to verify 1 conforms to json schema 'fred' because\n1 is not a string.''',repr(str(e))
        pass
    try:
        Schema('fred').validate('jock')
        assert None
    except Exception,e:
        assert str(e)=='''Failed to verify 'jock' conforms to json schema 'fred' because\n'jock' is not 'fred'.''',repr(str(e))
        pass
    try:
        Schema({'a':IntType,'c':IntType}).validate({'a':1})
    except Exception,e:
        assert str(e)=='''Failed to verify {'a': 1} conforms to json schema {'a': <type 'int'>, 'c': <type 'int'>} because\n'c' is missing.''',repr(str(e))
    else:
        assert None
        pass

if __name__=='__main__':
    test()
