# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

# ---------- General Exceptions ----------
class InvalidFormClass(Exception):
    """
    Form exception for invalid component wrapper class.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidFormClass, self).__init__(message)

class ExpressionCompileError(Exception):
    """
    Exception related to expression errors.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(ExpressionCompileError, self).__init__(message)

# ---------- Field Exceptions ----------
class FieldDefinitionError(Exception):
    """
    Form field definition error.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(FieldDefinitionError, self).__init__(message)

class FieldValueError(Exception):
    """
    Answer value does not matches with expected form field type.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(FieldValueError, self).__init__(message)

# ---------- Condition Exceptions ----------
class ConditionDefinitionError(Exception):
    """
    Condition definition is incorrect.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(ConditionDefinitionError, self).__init__(message)

# ---------- Layout Exceptions ----------
class LayoutDefinitionError(Exception):
    """
    Layout definition is incorrect.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(LayoutDefinitionError, self).__init__(message)

# ---------- Schema Exceptions ----------
class InvalidFormSchemaError(Exception):
    """
    Form schema has some errors.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidFormSchemaError, self).__init__(message)

# ---------- Widget Exceptions ----------
class InvalidWidgetError(Exception):
    """
    Form field widget is invalid.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidWidgetError, self).__init__(message)

# ---------- Variable Exceptions ----------
class InvalidConstantSchema(Exception):
    """
    Constant schema for the form is incorrect.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidConstantSchema, self).__init__(message)

class VariableDefinitionError(Exception):
    """
    Form variable definition is incorrect.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(VariableDefinitionError, self).__init__(message)

class InvalidCalculatedFieldSchema(Exception):
    """
    Calculated fields schema is incorrect.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidCalculatedFieldSchema, self).__init__(message)

class InvalidCalculatedFieldExpression(Exception):
    """
    Calculated field expression is incorrect.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(InvalidCalculatedFieldExpression, self).__init__(message)

class DuplicateVariableName(Exception):
    """
    Variable name is duplicate.

    **Authors**: Gagandeep Singh
    """
    def __init__(self, message):
        super(DuplicateVariableName, self).__init__(message)