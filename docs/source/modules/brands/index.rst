Brands
======

App to mange brands. This app takes care of all brand related use cases such as creation, ownership, verification etc.

Operations
----------
This section discusses various heavy operations related to the brand. Each of these operations consist of small
task executed sequentially in a flow.

1. New Brand Creation
~~~~~~~~~~~~~~~~~~~~~
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



Contents
--------

    .. toctree::
       :maxdepth: 2
       :titlesonly:

       models
       forms
       operations
       api

