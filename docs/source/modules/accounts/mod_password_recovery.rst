Password Recovery
=================

The flow for password recovery or password creation (in case password was not set earlier since user registered from mobile)
is mostly divided into two process; Plea for password recovery to obtain verification code and then reset with new password
using the same code.


.. note::
    Only **'Verified'** and **'Unverified'** are allowed to recover password.


1. Password recovery plea
-------------------------
User clicks password recovery by providing his mobile number (username). User classification is checked and password
reset code is send using SMS or email.

    .. image:: ../../_static/accounts/password_recovey_plea.jpg
        :scale: 80%
        :align: center

2. Recover account
------------------
After plea, user is provided with a recovery form where he enters the verification code along with new password.
User password is reset and is either automatically logged in to his account if verified or redirected to
registration verification page if unverified.

    .. image:: ../../_static/accounts/recover_account.jpg
        :scale: 80%
        :align: center