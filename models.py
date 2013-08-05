from ek import app, db
from flask.ext.security import UserMixin, RoleMixin, SQLAlchemyUserDatastore, Security


roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

categories_things = db.Table('categories_things',
        db.Column('category_id', db.Integer(), db.ForeignKey('category.id')),
        db.Column('thing_id', db.Integer(), db.ForeignKey('thing.id')))

objects_things = db.Table('objects_things',
        db.Column('object_id', db.Integer(), db.ForeignKey('object.id')),
        db.Column('thing_id', db.Integer(), db.ForeignKey('thing.id')))

users_things = db.Table('users_things',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('thing_id', db.Integer(), db.ForeignKey('thing.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __repr__(self):
        return self.name


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    name = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users, backref=db.backref('users', lazy='dynamic'))

    def __repr__(self):
        return self.name


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)

    def __repr__(self):
        return self.name


class Thing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    categories = db.relationship('Category', secondary=categories_things, backref=db.backref('things', lazy='dynamic'))

    def __repr__(self):
        return self.name


class Object(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship(User, backref='objects')
    thing_id = db.Column(db.Integer, db.ForeignKey('thing.id'))
    thing = db.relationship(Thing, backref='objects')

    def __repr__(self):
        return "%s's %s" % (self.owner, self.thing)

users = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, users)