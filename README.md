# dbCrud
a simple CRUD cycle in python cherrypy including the database creation and two tables, two triggers, a view and a stored procedure.

Server.py is the core of this simple application; when it starts, it create a database and two tables, "employee" and "office", it inserts three rows in "office" table and it creates a view as a join of them.
When index method is called, the server creates two triggers that don't allow to insert a negative value for the salary in create and update methods and a stored procedure to show the view in index page.

Before starting make sure that you entered the correct mysql credentials.

This is just an example but I hope it will be useful to someone.
Enjoy it!


For installing dependencies:

  pip install -r requirements.txt


(python version 3.9)
