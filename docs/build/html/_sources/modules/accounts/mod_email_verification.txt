Email Verification
==================

Email verification is a two stage process where a user first changes his/her email address and a verification link is
send to this new email. User then opens the verification from the mail and confirms himself before link is expired.

1. Update email address
-----------------------
From account settings user changes his email address and click 'Verify'. On backend request is received, verification
link is created and send to user's email address.

    .. note::
        At this point email address is not updated into user's profile. New email address is encoded inside the
        JSON Web Token inside the link.

    .. image:: ../../_static/accounts/email_change_flow.jpg
        :scale: 80%
        :align: center

2. Email verification
---------------------
After the user has submitted the request, he must now open his email in his email account, click the the link in the email
from where automatically make final changes in user account if the link is valid & within expiry tme.

    .. image:: ../../_static/accounts/email_verification_flow.jpg
        :scale: 80%
        :align: center