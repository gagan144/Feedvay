Organization
============

An organization is an legal registered entity such as Company, Firm, Agency, Government or non-government organization,
NGO etc. Such an organization can be Proprietorship, Partnership or Private Limited. These will have owners and
can be potential clients. All billing are attached to this entity if services are used under it.

1. Organisation registration or creation
----------------------------------------
There are many ways through which an organization can be registered or creating in the system:

A. Creation by staff
~~~~~~~~~~~~~~~~~~~~
Any staff member who has permission to create organization can create a new one. This allows flexibility
to create organization when a client opts for support service in terms of configurations.

B. Registration by user
~~~~~~~~~~~~~~~~~~~~~~~
Any registered user can register an organization through his management console. Such a user can
be the owner himself or might register on behave of his organization. The flow is as follows:

    1. The user fills a organization registration form. Provides name, logo, icons, type etc. He is
       also asked whether he is the owner or registering on behalf of his organization. After filling all
       details and agreeing to the terms, user submits the form.
    2. At backend, details are recieved and a new entry is made in :class:`market.models.Organization` with
       verification status as ``verification_pending``.
    3. Associate user with this organization. If he claims to be the owner, add him as owner.
    4. Respond to the user with message saying verification pending.

From here, user waits for verification to be completed. He can edit details if he wants and can also
explore various services.


2. Organization verification (By Staff)
---------------------------------------
One of the staff member who is responsible to authenticate organization will pick up pending
organization and verify the details. This might require him to contact the creator and perform
a call verification. After that, user has choice to reject and mark it verified. Appropriate
notifications are send to the owners.

3. Re-registration
------------------
If an organization has been rejected, user can re-register by submitting corrected information
as specified in reason for rejection. To do this:

    - User goes to organization settings and edit his previous details and submits.
    - At backend, all changes are updated in the organization instance itself **(inplace update)**
     and organization is transitioned to ``verification_pending`` state.

From here, user again waits for the verification to be completed.


4. Organization change/edit
~~~~~~~~~~~~~~~~~~~~~~~~~~~
User can edit or update information however, change is not immediate. When user
submits a change, all changes are recorded as change request which are verified and then migrated.

       - User edits organization information from settings and submits request after reviewing.
       - At backend, request is received and validated.
       - If organization status is ``verification_pending``, updates are made immediately in the model **(Inplace)**.
       - However, if status is ``verified``, all changes are stored in a separate model
         which are then migrated or rejected after manual evaluation.


5. User disassociation from organization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
A user can only be disassociated by a user higher in hierarchy.