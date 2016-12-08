# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from jsonobject import *
import uuid

from form_builder.utils import JsCompilerTool
from form_exceptions import *
import layouts

# ---------- Generic Condition ----------
# Points:
# * Add new layout:
#   - Extend BaseCondition class
#   - For naming use convention '<name>Condition'; It must contain word Condition in the end
#   - Add check condition in following routine:
#       - form_builder.models.iterate_form_fields()
#       - /form_builder/templates/form_builder/form_designer.html -> get_variable_with_id()
#   - Form designer: create partial templates for this condition:
#       /static/templates/form_builder/
#           |--- look-n-feel
#           |       |--- <class_name>.html
#           |--- editor
#                   |--- <class_name>.html
#       form_builder.templates
#           /form_builder/form_designer.html
#               Controller: QuestionSchemaController, inside '$scope.remove_condition'
#                   Add condition to remove all translation when this condition is deleted
#   - Form:
#       /form_builder/templates/themes/form_base.html
class BaseCondition(JsonObject):
    """
    A condition describes a control flow depending upon an expression evaluation. This implements a branching mechanism, determining
    which path to flow when expressions evaluates a result.
    Use this class to inherit and define specific flow controls.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    _cls_base = StringProperty(default='BaseCondition', required=True)
    _cls = StringProperty(name='_cls', required=True)
    _id = StringProperty(name='_id', required=True)
    name = StringProperty()
    is_advance = BooleanProperty(default=False, required=True)  # Used in form designer; if true use writes complex condition code else uses UI to generate simple expressions
    expression = StringProperty(required=True)      # Condition expression (In Javascript)
    lock_expression = BooleanProperty(default=False, required=True) # If true, expression cannot be editted in form designer
    validate_expr_var = BooleanProperty(required=True, default=False)   # Validate every variable in the expression to be not null
    user_notes = StringProperty()       # User notes for this conditions

    @property
    def expression_validate_var(self):
        """
        Returns a javascript expression that checks all variables in the expression to be not null.
        This is used when 'validate_expr_var' is set true. In this case true/false branch is shown in the form
        only if and only if this expression evaluates to true. Otherwise nothing happens.

        :return: Javascript expression

        **Authors**: Gagandeep Singh
        """

        jscompiler = JsCompilerTool(self.expression)
        list_vars = jscompiler.extract_variables()

        validate_expr = []
        for var in list_vars:
            if var.__contains__('data.') or var.__contains__('constants.'):
                validate_expr.append("{} == null".format(var))
        validate_expr = '!({})'.format(' || '.join(validate_expr))
        return validate_expr


    def __init__(self, _obj=None, **kwargs):
        # (1) Check '_cls' in _obj or kwargs
        this_class = self.__class__.__name__
        obj_cls = None
        if _obj is not None:
            obj_cls = _obj.get('_cls',None)
        else:
            obj_cls = kwargs.get('_cls',None)

        if obj_cls:
            if obj_cls != this_class:
                raise ConditionDefinitionError("Condition class mismatch. Using class '{}'".format(obj_cls))
        else:
            obj_cls = this_class

        # (2) Check '_id' on _obj & kwargs
        cond_id = None
        if _obj is not None:
            cond_id = _obj.get('_id',None)
        else:
            cond_id = kwargs.get('_id',None)

        if cond_id is None:
            cond_id = str(uuid.uuid4())

        # Update kwargs
        kwargs.update({
            "_cls": obj_cls,
            "_id": cond_id
        })
        super(BaseCondition, self).__init__(_obj=_obj, **kwargs)

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self._id)

    def get_id(self):
        return self._id

# ---------- /Generic Condition ----------

class BinaryCondition(BaseCondition):
    """
    Defines a binary branch with two possible paths (or just one), one for expression is 'true' and other for 'false'.
    A false branch can be skipped.

    **Authors**: Gagandeep Singh
    """
    true_branch = ObjectProperty(layouts.SectionLayout,required=True)
    false_branch = ObjectProperty(layouts.SectionLayout, default=None)

class SwitchCondition(BaseCondition):
    """
    Defines a 1xN Multiplier that selects one of the seleveral branches depending upon the expression.
    Here expression is usually a value of the field having many possible results/cases. Depending upon the
    value, corresponding branch is selected.

    **Authors**: Gagandeep Singh
    """

    list_cases = ListProperty(required=True)        # List of possible values
    list_branches = ListProperty(layouts.SectionLayout, required=True)  # List of corresponding conditions.
    use_default = BooleanProperty(required=True, default=False)     # Use default case if expression does not matches any values in 'list_cases'
    default_branch = ObjectProperty(layouts.SectionLayout, default=None)      # Branch for default case if 'user_deafult' is selected

    def __init__(self, _obj=None, **kwargs):
        super(SwitchCondition,self).__init__(_obj=_obj, **kwargs)

        # Check if 'list_cases' & 'list_branches' are of equal length
        if len(self.list_cases) != len(self.list_branches):
            raise ConditionDefinitionError("'list_cases' doesn't seems to be of equal length with 'list_branches'")

        # Check 'default_branch'
        if self.use_default:
            if self.default_branch is None:
                raise ConditionDefinitionError("Default branch required since 'use_default' is checked.")

    def iterate_branch(self):
        for case,branch in zip(self.list_cases, self.list_branches):
            yield case, branch

# ---------- Methods ----------
def create_condition_obj(condition_dict):
    """
    Converts a condition dictionary into condition object.
    :param condition_dict: dict
    :return: Condition Object

    **Authors**: Gagandeep Singh
    """
    class_name = condition_dict['_cls']
    try:
        condition_obj = globals()[class_name](condition_dict)
        return condition_obj
    except:
        raise InvalidFormClass("'{}' is not a valid condition class.".format(class_name))

