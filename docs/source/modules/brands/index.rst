Brands
======

App to mange brands. This app takes care of all brand related use cases such as creation, ownership, verification etc.

Operations
----------
This section discusses various heavy operations related to the brand. Each of these operations consist of small
task executed sequentially in a flow.

1. Create new brand
~~~~~~~~~~~~~~~~~~~
This operation defines the flow to create a new brand. A new brand can be created by a registered user or a staff user.

       - Creation by registered user: For a registered user creation of brand typically means submitting a request
          for new brand. The flow is as follows:

              - User fills a form by providing necessary details such as name, description, logo etc and submits it with
                self as owner of the brand.
              - At backend, validated submitted details.
              - Create entry in :class:`brands.models.Brand` is with status ``verification pending``.
              - Create entry in :class:`brands.models.BrandOwner` to make user as brand owner.
              - Return with appropriate message.

          From here, user waits for the verification to be completed. However, he can continue working within
          the brand to associate POBS etc.

3. Re-register brand (after rejection)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If a brand has been rejected, user can re-register his brand by submitting corrected information
as specified in reason for failure. To do this:

       - User goes to brand settings and edit his previous details about the brand and submits.
       - At backend, all changes are updated in the brand instance itself **(inplace update)**
         and brand is transitioned to ``verification_pending`` state.

       From here, user waits for the verification to be completed.


4. Brand change/edit
~~~~~~~~~~~~~~~~~~~~
User can edit or update information about his brand. However, change is not immediate. When user
submits a change, all changes are recorded as change request which are verified and then migrated.

       - User edits brand information from settings and submits request after reviewing.
       - At backend, request is received and validated.
       - If brand status is ``verification_pending``, updates are made immediately in made model **(Inplace)**.
       - However, if status is ``verified``, all changes are stored in a separate model :class:`brands.models.BrandChangeRequest`
         which are then migrated or rejected after manual evaluation.


5. Brand disassociation
~~~~~~~~~~~~~~~~~~~~~~~
All owners have provision to give up his ownership over a brand. If user is no longer
associated to the brand (in real world), he can release ownership by:

       - Going to brand settings > Ownership.
       - Here user has option to relase ownership.
       - After confirmation, user submits request.
       - At backend, user entry is **removed** from :class:`brands.models.BrandOwner` model.
       - Owls are send to disassociating user and all owners.

Once ownership is given up, user has no authority over the brand. This action is irreversible.


Contents
--------

    .. toctree::
       :maxdepth: 2
       :titlesonly:

       models
       forms
       operations
       api

