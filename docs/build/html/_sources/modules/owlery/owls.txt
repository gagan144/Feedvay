Owls
====

An owl is an entity responsible for handling messages of its kind (SMS, email etc).
Each owl defines a set of message handlers with a templates that can be used to along with
associated parameters to send a message.

Messages are mostly handled asynchronously. That means as you call one of the handler, message is composed
and stored in database for some independent process to pick up and dispatch it.

**Guidelines**:
    - For every communication kind (SMS, email) an owl class is created.
    - Inside this class, methods are defined that actually compose a message given a set of
      parameters, create database entries and return its instance. An example can be a handler to
      send message for registration verification or success.
      Any error or failure occurred must be thrown as an exception.
    - These handler methods may or may not send message immediately and mostly rely on some
      independent process to send them.


.. automodule:: owlery.owls
    :members:

