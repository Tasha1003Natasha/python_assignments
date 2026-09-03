Contacts REST API
=================

Documentation for the FastAPI application that manages contacts and users.
The application provides authentication, email verification, password reset,
contact search, birthday reminders, Redis rate limiting, and avatar uploads.

.. toctree::
  :maxdepth: 2
  :caption: Documentation sections

Application
-----------

The main FastAPI application and router configuration.

.. automodule:: main
  :members:
  :undoc-members:

API Routes
----------

Authentication and account management endpoints.

.. automodule:: src.routes.auth
  :members:
  :undoc-members:

Contact management endpoints.

.. automodule:: src.routes.contacts
  :members:
  :undoc-members:

User profile and avatar endpoints.

.. automodule:: src.routes.users
  :members:
  :undoc-members:

Schemas and Models
------------------

Request and response schemas for contacts.

.. automodule:: src.schemas.contact
  :members:
  :undoc-members:

Request and response schemas for users and authentication.

.. automodule:: src.schemas.user
  :members:
  :undoc-members:

SQLAlchemy models for users and contacts.

.. automodule:: src.entity.models
  :members:
  :undoc-members:

Repositories
------------

Database operations for contacts.

.. automodule:: src.repository.contacts
  :members:
  :undoc-members:

Database operations for users.

.. automodule:: src.repository.users
  :members:
  :undoc-members:

Services
--------

Authentication and JWT services.

.. automodule:: src.services.auth
  :members:
  :undoc-members:

Email delivery and notification services.

.. automodule:: src.services.email
  :members:
  :undoc-members:

Rate limiting services.

.. automodule:: src.services.rate_limiter
  :members:
  :undoc-members:

Role-based access control services.

.. automodule:: src.services.roles
  :members:
  :undoc-members:

Database and Configuration
--------------------------

Async database connection and session management.

.. automodule:: src.database.db
  :members:
  :undoc-members:

Application settings loaded from environment variables.

.. automodule:: src.conf.config
  :members:
  :undoc-members:

Indices and Tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
