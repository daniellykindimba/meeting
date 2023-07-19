import graphene


class JSON(graphene.Scalar):
    @staticmethod
    def identity(value):
        if isinstance(value, (str, bool, int, float)):
            return value.__class__(value)
        elif isinstance(value, (list, dict)):
            return value
        else:
            return None

    serialize = identity
    parse_value = identity

    @staticmethod
    def parse_literal(ast):
        if isinstance(ast, (StringValue, BooleanValue)):
            return ast.value
        elif isinstance(ast, IntValue):
            num = int(ast.value)
            if MIN_INT <= num <= MAX_INT:
                return num
        elif isinstance(ast, FloatValue):
            return float(ast.value)
        elif isinstance(ast, ListValue):
            return [JSON.parse_literal(value) for value in ast.values]
        elif isinstance(ast, ObjectValue):
            return {field.name.value: JSON.parse_literal(field.value) for field in ast.fields}
        else:
            return None