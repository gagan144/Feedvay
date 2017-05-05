Project Theme
=============

The entire project is based on bootstrap responsive theme applicable for all kinds of devices such as desktop & mobile.
Currently Feedvay uses purchased licensed of bootstrap based theme `Inspinia <https://wrapbootstrap.com/theme/inspinia-responsive-admin-theme-WB0R5L90S>`_
and make some custom changes in the seed in terms of component look-n-feel and theme colors.

Also, one of the features that Feedvay offers is custom skin for each brand. Brand owners can change color of the
theme as per their branding. This gives a nice, customized, brand specific portal view.


Custom skins
------------
A skin is usually a small variation in the main theme in terms of colors and minor changes. A skin does not changes
basic look-n-feel of the components. So, for a theme there can be many skins.

Since each brand can define its own skin, a structure has been defined to generate custom skin as well as Feedvay signature theme.

All theme files (css, js etc) are placed in '/static/ui/' directory of the project. This directory has a main theme file
(style-default.css) which is static. This file is never edited manually, rather generated using django command.

.. warning::
    **DO NOT** edit '/static/ui/style-default.css' manually. This must be generated using django command.

To edit a skin, a template file has been created using the theme default skin which has placeholders for customizations.
Django template rendering module is used to read this file and fill placeholders based on parameters.

The template file is placed in the template directory '/templates/theme/inspinia-style-template.css' and
the parameters are as follows:

+----------------------+--------------------------------------------------------------------------+
| Parameter            | Remarks                                                                  |
+======================+==========================================================================+
| primary              | Primary color of the skin; primary text, buttons, nav bars etc.          |
+----------------------+--------------------------------------------------------------------------+
| primary_dark         | Darker version of primary color. Used for mouse hovers etc.              |
+----------------------+--------------------------------------------------------------------------+
| primary_disabled     | Transparent look of primary color used for disabled components.          |
+----------------------+--------------------------------------------------------------------------+

A function **render_theme** has been defined in
**Utilities** app that uses the template skin file and returns the content of the customized theme file
that is stored in a css file for later use.

For Feedvay signature theme, parameters are defined by ``THEME_DEFAULT`` in ``settings.py`` file and a django
management command is used to generates the skin which automatically updates '/static/ui/style-default.css'.

.. note::
    To make any changes in the **Theme**, edit '/templates/theme/inspinia-style-template.css' and call
    django management command **feedvay_update_theme_skins**
    to make changes in feedvay and all brands skin:

        >>> python manage.py feedvay_update_theme_skins
