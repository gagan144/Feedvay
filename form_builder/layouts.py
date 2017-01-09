# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.

from jsonobject import *
import uuid

from form_exceptions import *
from fields import create_field_obj

# ---------- Generic Layout ----------
# Points:
# * Add new layout:
#   - Extend BaseLayout class
#   - For naming use convention '<name>Layout'; It must contain word Layout in the end
#   - Add check condition in following routine:
#       - form_builder.models.iterate_form_fields()
#       - /form_builder/templates/form_builder/form_designer.html -> get_variable_with_id()
#   - Form designer: create partial templates for this layout:
#       /static/templates/form_builder/
#           |--- look-n-feel
#           |       |--- <class_name>.html
#           |--- editor
#                   |--- <class_name>.html
#   - Form:
#       /form_builder/templates/themes/form_base.html
class BaseLayout(JsonObject):
    """
    A Layout defines an encapsulated arrangement of components (Fields, Conditions or even a layout).
    This is generic class which must be inherited to define specific layout.

    **Authors**: Gagandeep Singh
    """
    _allow_dynamic_properties = False

    _cls_base = StringProperty(default='BaseLayout', required=True)
    _cls = StringProperty(name='_cls', required=True)
    _id = StringProperty(name='_id', required=True)
    title = StringProperty()     # Title of the this section. If None, title is not displayed
    highlight_layout = BooleanProperty(required=True,default=True)    # Whether to highlight this section with outlines or not
    children = ListProperty(required=True)      # List of children (only Fields/Conditions) encapsulated in this layout.

    @property
    def children_obj(self):
        from conditions import create_condition_obj
        list_obj = []
        for node_dict in self.children:

            if node_dict['_cls_base'] == 'BasicFormField':
                node_obj = create_field_obj(node_dict)
            elif node_dict['_cls_base'] == 'BaseCondition':
                node_obj = create_condition_obj(node_dict)
            else:
                raise InvalidFormClass("Unknown field or condition class {}".format(node_dict['_cls']))

            """
            # Try as field
            try:
                node_obj = create_field_obj(node_dict)
            except InvalidFormClass:
                # Try as condition
                try:
                    node_obj = create_condition_obj(node_dict)
                except InvalidFormClass:
                    raise InvalidFormClass("Unknown field or condition class {}".format(node_dict['_cls']))
            """

            list_obj.append(node_obj)

        return list_obj


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
                raise LayoutDefinitionError("Layout class mismatch. Using class '{}'".format(obj_cls))
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
        super(BaseLayout, self).__init__(_obj=_obj, **kwargs)

        # Check 'children'
        # import form_schema

    def __str__(self):
        return "<{}: {}>".format(self.__class__.__name__, self._id)

    def get_id(self):
        return self._id

# ---------- /Generic Layout ----------


class SectionLayout(BaseLayout):
    """
    Defines a division or a section in a form

    **Authors**: Gagandeep Singh
    """



# ---------- Methods ----------
def create_layout_obj(layout_dict):
    """
    Converts a field dictionary into a corresponding field object.

    :param condition_dict: dict
    :return: Layout Object

    **Authors**: Gagandeep Singh
    """
    class_name = layout_dict['_cls']
    try:
        layout_obj = globals()[class_name](layout_dict)
        return layout_obj
    except:
        raise InvalidFormClass("'{}' is not a valid layout class.".format(class_name))