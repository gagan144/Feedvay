# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

import json

from form_builder.form_exceptions import InvalidCalculatedFieldSchema
from form_builder.form_variables import create_calculated_field_obj
from form_exceptions import InvalidFormSchemaError, InvalidFormClass, InvalidConstantSchema
from fields import create_field_obj
from conditions import create_condition_obj
from layouts import create_layout_obj
from form_variables import create_constant_obj


def load_form_class(node_dict):
    """
    Accepts a dict and convert it into form class object.

    :param class_dict: dict

    **Authors**: Gagandeep Singh
    """

    class_name = node_dict['_cls']
    node_obj = None

    # Try as field
    try:
        node_obj = create_field_obj(node_dict)
    except InvalidFormClass:
        # Try as Condition
        try:
            node_obj = create_condition_obj(node_dict)
        except InvalidFormClass:
            # Try as Layout
            try:
                node_obj = create_layout_obj(node_dict)
            except InvalidFormClass:
                raise InvalidFormClass("Unknown class {}".format(class_name))

    return node_obj


def load_form_schema(schema):
    """
    Accepts json or json string of form json and returns object schema.
    If schema is list, it is treated as form schema.
    If schema is dict, it is treated as form class schema, which will return object of that class

    :param schema: list/str
    :return: object schema

    **Authors**: Gagandeep Singh
    """

    schema_object = None

    if isinstance(schema, str):
        schema = json.loads(schema)
    elif isinstance(schema, dict) or isinstance(schema, list):
        pass
    else:
        raise InvalidFormSchemaError("Schema must be a type list, dict or str.")

    # Convert to object accordingly
    if isinstance(schema, dict):
        pass
    elif isinstance(schema, list):
        schema_object = []
        for node_dict in schema:
            node_obj = load_form_class(node_dict)
            schema_object.append(node_obj)

    #print schema
    return schema_object

def load_constant_schema(schema):
    """
    Accepts a list json or a equivalent string and converts into list of 'form_variables.Constant'.

    **Authors**: Gagandeep Singh
    """
    if isinstance(schema, str):
        schema = json.loads(schema)
    elif isinstance(schema, list):
        pass
    else:
        raise InvalidConstantSchema("Constant schema must be a type list or str.")

    constant_schema_obj = []
    for constant_dict in schema:
        constant_schema_obj.append(
            create_constant_obj(constant_dict)
        )

    return constant_schema_obj

def load_calculated_fields_schema(schema):
    """
    Accepts a list json or a equivalent string and converts into list of 'form_variables.CalculatedField'.

    **Authors**: Gagandeep Singh
    """
    if isinstance(schema, str):
        schema = json.loads(schema)
    elif isinstance(schema, list):
        pass
    else:
        raise InvalidCalculatedFieldSchema("Calculated field schema must be a type list or str.")

    calc_fld_schema_obj = []
    for calc_fld_dict in schema:
        calc_fld_schema_obj.append(
            create_calculated_field_obj(calc_fld_dict)
        )

    return calc_fld_schema_obj

