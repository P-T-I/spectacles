from flask_avatars import Identicon
from flask_login import UserMixin
from werkzeug.security import generate_password_hash

from spectacles.webapp.run import db


class users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(48), unique=True)
    email = db.Column("email", db.String(48))
    password = db.Column("password", db.String(512))
    status = db.Column("status", db.Integer, default=0)
    role = db.Column("role", db.String(16), default="user")
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    group_member = db.relationship("groupmembers", backref="user", lazy="dynamic")
    claims = db.relationship("claims", backref="user", lazy="dynamic")

    def hash_password(self, password):
        """
        Method to hash the password

        :param password: Password given
        :type password: str
        :return: Hashed password
        :rtype: str
        """
        self.password = generate_password_hash(password, method="pbkdf2:sha512")

    def user_to_dict(self):

        user_dict = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "status": self.status,
            "avatar": self.avatar_l,
        }

        return user_dict

    def generate_avatar(self):
        avatar = Identicon()
        try:
            filenames = avatar.generate(text=self.username)
            self.avatar_s = filenames[0]
            self.avatar_m = filenames[1]
            self.avatar_l = filenames[2]
            db.session.commit()
        except FileNotFoundError:
            pass


class group(db.Model):
    __tablename__ = "group"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(256))
    members = db.relationship("groupmembers", backref="group", lazy="dynamic")
    claims = db.relationship("claims", backref="group", lazy="dynamic")
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)


class groupmembers(db.Model):
    __tablename__ = "groupmembers"
    id = db.Column("id", db.Integer, primary_key=True)
    groupid = db.Column(
        "groupid",
        db.Integer,
        db.ForeignKey("group.id", ondelete="cascade", onupdate="cascade"),
    )
    userid = db.Column("userid", db.Integer, db.ForeignKey("users.id"))


class registry(db.Model):
    __tablename__ = "registry"
    id = db.Column("id", db.Integer, primary_key=True)
    uri = db.Column("uri", db.String(128))
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    content = db.relationship("repository", backref="registry", lazy="dynamic")


class repository(db.Model):
    __tablename__ = "repository"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(512))
    registryid = db.Column(
        "registryid",
        db.Integer,
        db.ForeignKey("registry.id", ondelete="cascade", onupdate="cascade"),
    )
    ownerid = db.Column(
        "ownerid",
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
    )
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    claims = db.relationship("claims", backref="repository", lazy="dynamic")


class tags(db.Model):
    __tablename__ = "tags"
    id = db.Column("id", db.Integer, primary_key=True)
    version = db.Column("version", db.String(128), default="latest")
    repositoryid = db.Column(
        "repositoryid",
        db.Integer,
        db.ForeignKey("repository.id", ondelete="cascade", onupdate="cascade"),
    )
    digest = db.Column("digest", db.String(512), default="0")
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)


class claims(db.Model):
    __tablename__ = "claims"
    id = db.Column("id", db.Integer, primary_key=True)
    claim = db.Column("claim", db.String(16), default="READ")
    repositoryid = db.Column(
        "repositoryid",
        db.Integer,
        db.ForeignKey("repository.id", ondelete="cascade", onupdate="cascade"),
    )
    groupid = db.Column(
        "groupid",
        db.Integer,
        db.ForeignKey("group.id", ondelete="cascade", onupdate="cascade"),
    )
    userid = db.Column(
        "userid",
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
    )
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
