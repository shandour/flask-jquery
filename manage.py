# -*- coding: utf-8 -*-
from flask_script import Manager, Server
from flask_security.utils import hash_password

from projecto import create_app
from projecto.models import db, User, Role
from projecto.security import ADMIN_ROLE, EDITOR_ROLE
from create_fixtures import create_fixtures


manager = Manager(create_app)


@manager.command
def create_db():
    "Creates the database"

    db.create_all()

    db.session.add_all(
        [Role(name=ADMIN_ROLE, description='The site Deity'),
         Role(name=EDITOR_ROLE, description='Can add and edit items')]
    )
    db.session.commit()


@manager.command
def drop_db():
    "Drops the database"

    db.drop_all()


@manager.option('-i', '--iteration_number',
                dest='creation_iteration_number',
                type=int,
                default=100)
@manager.option('-un', '--users_number',
                dest='users_number',
                type=int,
                default=10)
def create_db_fixtures(creation_iteration_number, users_number):
    "Creates fixtures"
    create_fixtures(creation_iteration_number, users_number)


@manager.option('-u', '--username', dest='username')
@manager.option('-e', '--email', dest='email')
@manager.option('-p', '--password', dest='password')
@manager.option('-r', '--role', dest='role', default=None)
def add_user(username, email, password, role):
    "Creates an admin, an editor a basic level (if role is None) user"
    message = ''

    user = User(
        username=username,
        email=email,
        password=hash_password(password),
        active=True
    )

    if role:
        if role.lower() == EDITOR_ROLE.lower():
            user.roles.append(Role.query.filter_by(name=EDITOR_ROLE).one())
            message = 'Editor created'
        elif role.lower() == ADMIN_ROLE.lower():
            user.roles.append(Role.query.filter_by(name=ADMIN_ROLE).one())
            message = 'Admin created'
    else:
        message = 'User created'

    db.session.add(user)
    db.session.commit()
    return message


manager.add_command('runserver', Server())

if __name__ == '__main__':
    manager.run()
