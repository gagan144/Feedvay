# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

# ---------- General Exceptions ----------
class InvalidFormClass(Exception):
    def __init__(self, message):
        super(InvalidFormClass, self).__init__(message)

class ExpressionCompileError(Exception):
    def __init__(self, message):
        super(ExpressionCompileError, self).__init__(message)

# ---------- Field Exceptions ----------
class FieldDefinitionError(Exception):
    def __init__(self, message):
        super(FieldDefinitionError, self).__init__(message)

class FieldValueError(Exception):
    def __init__(self, message):
        super(FieldValueError, self).__init__(message)

# ---------- Condition Exceptions ----------
class ConditionDefinitionError(Exception):
    def __init__(self, message):
        super(ConditionDefinitionError, self).__init__(message)

# ---------- Layout Exceptions ----------
class LayoutDefinitionError(Exception):
    def __init__(self, message):
        super(LayoutDefinitionError, self).__init__(message)

# ---------- Schema Exceptions ----------
class InvalidFormSchemaError(Exception):
    def __init__(self, message):
        super(InvalidFormSchemaError, self).__init__(message)

# ---------- Widget Exceptions ----------
class InvalidWidgetError(Exception):
    def __init__(self, message):
        super(InvalidWidgetError, self).__init__(message)

# ---------- Variable Exceptions ----------
class InvalidConstantSchema(Exception):
    def __init__(self, message):
        super(InvalidConstantSchema, self).__init__(message)

class VariableDefinitionError(Exception):
    def __init__(self, message):
        super(VariableDefinitionError, self).__init__(message)

class InvalidCalculatedFieldSchema(Exception):
    def __init__(self, message):
        super(InvalidCalculatedFieldSchema, self).__init__(message)

class InvalidCalculatedFieldExpression(Exception):
    def __init__(self, message):
        super(InvalidCalculatedFieldExpression, self).__init__(message)

class DuplicateVariableName(Exception):
    def __init__(self, message):
        super(DuplicateVariableName, self).__init__(message)