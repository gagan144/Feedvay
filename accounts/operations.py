# Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
# Content in this document can not be copied and/or distributed without the express
# permission of Gagandeep Singh.
from django.db import transaction

from django.contrib.auth.models import User

from accounts.models import RegisteredUser, UserProfile

def create_new_registered_user(username, form_data, reg_method, set_passwd=True):
    """
    Method to create a new registered user in the system.

    .. note::
        This method is one complete atomic process except for
        :class:`accounts.models.UserProfile` since it is mongoDb collection.

    :param username: Valid username of form ``<country_tel_code>-<mobile-no>``
    :param form_data: Dictionary with all relevant data
    :param reg_method: Registration method as per :py:data:`accounts.models.RegisteredUser.CH_REG_METHOD`
    :param set_passwd: If True, sets password as in form_data  and tranit reg_user to verification pending state. Ignores if False.
    :return: Newly created :class:`accounts.models.RegisteredUser` instance

    **Authors**: Gagandeep Singh
    """

    # Create all database entries in one atomic process
    with transaction.atomic():
        # Create 'User' model
        new_user = User.objects.create(
            username = username,
            first_name = form_data['first_name'],
            last_name = form_data['last_name'],
            is_active = False
        )

        # Create 'RegisterUser'
        new_registered_user = RegisteredUser.objects.create(
            user = new_user,
            reg_method = reg_method #RegisteredUser.REG_WEB_PORTAL
        )

        # Set password
        if set_passwd:
            new_registered_user.set_password(form_data['password'], send_owls=False) # This will save user

        # Create 'UserProfile'
        user_profile = UserProfile(
            registered_user_id = new_registered_user.id
        )
        user_profile.add_update_attribute('first_name', new_user.first_name, auto_save=False)
        user_profile.add_update_attribute('last_name', new_user.last_name, auto_save=False)
        if form_data.has_key('date_of_birth'):
            # user_profile.add_update_attribute('date_of_birth', form_reg.get_date_of_birth(), auto_save=False)
            user_profile.add_update_attribute('date_of_birth', form_data['date_of_birth'], auto_save=False)
        if form_data.has_key('gender'):
            user_profile.add_update_attribute('gender', form_data['gender'], auto_save=False)
        user_profile.save()

        if set_passwd:
            # Transit status from 'lead' to 'verification_pending'
            if new_registered_user.status == RegisteredUser.ST_LEAD:
                new_registered_user.trans_registered()
                new_registered_user.save()

        return new_registered_user