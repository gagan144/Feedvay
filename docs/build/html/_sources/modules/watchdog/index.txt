Watchdog
========

Watchdog as the name suggest is an app responsible to watch over the health of the system.
This app takes care of logging and maintaining track of all errors occurring in the system at runtime as well as errors reported by the users.
This app is also responsible for handling beta users to provide thier suggestions on the system

Features
--------
    - **Error Log**:
        Automatically logs any error that occurred in the system at runtime using a middleware.
        It keeps a track of error source in terms of server name & url, user that must have seen this error, error type, traceback,
        number of times seen and staff user that handled it.

    - **Reported Problems**:
        Error that have been reported by the user on all platforms.
        Error maintenance, link them to 'Error Log' if applicable, current status etc

    - **Suggestions**:
        These include open improvement suggestions made by user on any area of the system. This is used to grab requirements
        and user feedback about the system


Contents
--------

    .. toctree::
       :maxdepth: 2
       :titlesonly:

       models
       middleware

