Console
=======

Feedvay management console for authenticated registered user to allow them to use and manage various services
offered by feedvay such as feedback, survey design and publish, account management, team collaboration etc.

This is main console using which user can manage his entire operations on feedvay platform.


User and brand console url routing mechanism
--------------------------------------------

Management console is meant for both individual user as well as for brand. When a user logs in, he lands in his own
management console where he can manage surveys, POBS, account settings etc. However, a user may be associated to a brand
and wants to manage feedback, survey, POBS etc in context to the brand instead of his own. In such as case provision is provided
so that user can switch the context easily without having to go to different domain or url.

To create ease for both user and infrastructure implementation, a small routing mechanism has be implemented using django middleware
that uses same view for both user and brand related url.

       - All management console url begins with ``/console/``. By default, this leads to user console.
       - However, if a url begins with ``/console/b/<brand_uid>/``, this routes to brand console.
       - The purpose of the middleware is to make use of same view for both context. For instance consider an url
         that opens dashboard for currently running surveys, then url for user (as individual) would be
         ``/console/survey/`` and url for brand to which he is associated would be ``/console/b/brand-uid/survey/``.
         Here the purpose of both url is to manage survey but for different context.
       - The simplest way could be to define two different url entries in console.urls, one for user and other for brand and perhaps
         associate them to the same view. This introduces redundant work, messy urls which hard to maintain and prone to human error.
       - To overcome this problem, a middleware has be planted before resolving url that analyzes all console related url hits,
         identify if they are meant for user or brand:

              - If url is meant for brand i.e. url begins with ``/console/b/``, brand uid is extracted form the url path, brand is
                fetched from database, assigned to ``request.curr_brand`` for use in views & templates. Moreover, to resolve this
                request to the common view, ``/b/<brand_uid>/`` is removed from path before dispatching. For django URL dispatcher,
                path seems to be simple url (as if meant for user) for which there is associated view already defined which is
                called.
              - In case url is meant for user console, midlleware bypasses the request silently without any analysis.

       - All authentication & permission related check are taken care by the middleware as well.

Please refer to :class:`console.middleware.ConsoleBrandSwitchMiddleware` for further information.

.. warning::
       Across entire project, no url should begin with ``/console/b/``. This can confuse middleware and can lead to
       unusual behavior.


Contents
--------

    .. toctree::
       :maxdepth: 2
       :titlesonly:

       views
       middleware

