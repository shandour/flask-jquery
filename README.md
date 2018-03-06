# flask-jquery
A flask backend and jquery frontend library site.
A simple multi-page application using Flask, Flask-Security, Flask-SqlAlchemy, Flask-Wtforms, FLask-Navigation, sortedcontainers, Postgresql with indices and full-text search, Jinja and JQuery (making use of the MagicSuggest plugin).
Features:
* The Author and Book models representing teh main interactable entities, which can be added, deleted and edited (in case a user has the required permissions).
* The User and Role models used for authentication and authorization.
* A custom InfiniteLoad script used to load additional entities in case their numbers exceed the one specified in the app config. 
