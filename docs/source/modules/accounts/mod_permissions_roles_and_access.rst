User permissions, roles and access management
=============================================

This sections discusses architecture for **RegisteredUser** permissions for an **Organization**. All permissions, roles and
data access are always in context of organization only. Since a user can be associated to multiple organizations,
the user has multiple sets of permissions, roles and data access for that organization.

This module is inspired by django permission framework and uses the same concept but defining permissions in context of
an organization. It also expands the framework to defined permissions at resource level as well that is what data/record
instances are permitted to the user.

The basic idea behind user permissions is to obtain a permission JSON when required which can be easily looked up to
find a particular permission and data access. The data is stored in databases such that JSON can be easily and quickly
obtained at runtime with minimum operation cost. In order speed up the process and avoid unnecessary overheads, **caching**
is used to cache permission json and subsequent permission requests can be served from cache rather than hitting database.

Following diagram explains the architecture for permissions, roles and data access for a registered user only:

.. image:: ../../_static/accounts/user_role_and_access.jpg
        :scale: 90%
        :align: center


Obtain user permissions
-----------------------

For permission JOSN structure and methods to obtain permissions, kindly refer :class:`accounts.models.RegisteredUser` methods:

    - :py:func:`accounts.models.RegisteredUser.get_perm_cache_key`
    - :py:func:`accounts.models.RegisteredUser.fetch_all_permissions`
    - :py:func:`accounts.models.RegisteredUser.get_data_access`
    - :py:func:`accounts.models.RegisteredUser.get_all_permissions`
    - :py:func:`accounts.models.RegisteredUser.delete_permission_cache`


Django views decorator
----------------------

A decorator on every view that requires certain permissions to allow access.
Kindly refer the decorator :py:func:`accounts.decorators.organization_console`.

