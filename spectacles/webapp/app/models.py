from flask_avatars import Identicon
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from spectacles.webapp.run import db


class users(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column("id", db.Integer, primary_key=True)
    username = db.Column("username", db.String(48), unique=True)
    email = db.Column("email", db.String(48))
    password_hash = db.Column("password", db.String(512))
    status = db.Column("status", db.Integer, default=0)
    role = db.Column("role", db.String(16), default="user")
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    group_member = db.relationship("groupmembers", backref="user", lazy="joined")
    namespaces = db.relationship("namespaces", backref="user", lazy="dynamic")
    namespacemembers = db.relationship(
        "namespacemembers", backref="user", lazy="dynamic"
    )
    claimmembers = db.relationship("claimsmembers", backref="user", lazy="joined")

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha512")

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

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


class groups(db.Model):
    __tablename__ = "groups"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(256), index=True, unique=True)
    description = db.Column("description", db.String(512))
    members = db.relationship("groupmembers", backref="group", lazy="dynamic")
    namespacegroups = db.relationship(
        "namespacegroups", backref="group", lazy="dynamic"
    )
    claimgroups = db.relationship("claimsgroups", backref="group", lazy="joined")
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)

    def group_dict(self):

        ret_dict = {"id": self.id, "name": self.name}

        return ret_dict


class groupmembers(db.Model):
    __tablename__ = "groupmembers"
    id = db.Column("id", db.Integer, primary_key=True)
    groupid = db.Column(
        "groupid",
        db.Integer,
        db.ForeignKey("groups.id", ondelete="cascade", onupdate="cascade"),
    )
    userid = db.Column(
        "userid",
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
    )


class registry(db.Model):
    __tablename__ = "registry"
    id = db.Column("id", db.Integer, primary_key=True)
    uri = db.Column("uri", db.String(128), index=True, unique=True)
    protocol = db.Column("protocol", db.String(16))
    service_name = db.Column("service_name", db.String(256))
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    content = db.relationship("namespaces", backref="registry", lazy="dynamic")

    def __repr__(self):
        return "{}".format(self.uri)


class namespaces(db.Model):
    __tablename__ = "namespaces"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(512), index=True, unique=True)
    description = db.Column("description", db.String(512))
    owner = db.Column(
        "owner",
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
    )
    registryid = db.Column(
        "registryid",
        db.Integer,
        db.ForeignKey("registry.id", ondelete="cascade", onupdate="cascade"),
    )
    P_claim = db.Column("P_claim", db.String(16), default="FULL")
    G_claim = db.Column("G_claim", db.String(16), default="NONE")
    O_claim = db.Column("O_claim", db.String(16), default="NONE")
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    repositories = db.relationship("repository", backref="namespace", lazy="dynamic")
    claims = db.relationship("claims", backref="namespace", lazy="dynamic")
    members = db.relationship("namespacemembers", backref="namespace", lazy="joined")
    groups = db.relationship("namespacegroups", backref="namespace", lazy="joined")


class repository(db.Model):
    __tablename__ = "repository"
    id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column("name", db.String(512), index=True)
    path = db.Column("path", db.String(512), index=True, unique=True)
    namespacesid = db.Column(
        "namespacesid",
        db.Integer,
        db.ForeignKey("namespaces.id", ondelete="cascade", onupdate="cascade"),
    )
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    tags = db.relationship("tags", backref="repository", lazy="dynamic")


class tags(db.Model):
    __tablename__ = "tags"
    id = db.Column("id", db.Integer, primary_key=True)
    version = db.Column("version", db.String(128), default="latest", index=True)
    repositoryid = db.Column(
        "repositoryid",
        db.Integer,
        db.ForeignKey("repository.id", ondelete="cascade", onupdate="cascade"),
    )
    digest = db.Column("digest", db.String(512), default="0")
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)


class namespacemembers(db.Model):
    __tablename__ = "namespacemembers"
    id = db.Column("id", db.Integer, primary_key=True)
    namespaceid = db.Column(
        "namespaceid",
        db.Integer,
        db.ForeignKey("namespaces.id", ondelete="cascade", onupdate="cascade"),
    )
    userid = db.Column(
        "userid",
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
    )


class namespacegroups(db.Model):
    __tablename__ = "namespacegroups"
    id = db.Column("id", db.Integer, primary_key=True)
    namespaceid = db.Column(
        "namespaceid",
        db.Integer,
        db.ForeignKey("namespaces.id", ondelete="cascade", onupdate="cascade"),
    )
    groupid = db.Column(
        "groupid",
        db.Integer,
        db.ForeignKey("groups.id", ondelete="cascade", onupdate="cascade"),
    )


class claims(db.Model):
    __tablename__ = "claims"
    id = db.Column("id", db.Integer, primary_key=True)
    claim = db.Column("claim", db.String(16), default="NONE")
    namespaceid = db.Column(
        "namespaceid",
        db.Integer,
        db.ForeignKey("namespaces.id", ondelete="cascade", onupdate="cascade"),
    )
    created = db.Column("created", db.Integer, default=0)
    updated = db.Column("updated", db.Integer, default=0)
    members = db.relationship("claimsmembers", backref="claims", lazy="joined")
    groups = db.relationship("claimsgroups", backref="claims", lazy="joined")


class claimsmembers(db.Model):
    __tablename__ = "claimsmembers"
    id = db.Column("id", db.Integer, primary_key=True)
    claimsid = db.Column(
        "claimsid",
        db.Integer,
        db.ForeignKey("claims.id", ondelete="cascade", onupdate="cascade"),
    )
    userid = db.Column(
        "userid",
        db.Integer,
        db.ForeignKey("users.id", ondelete="cascade", onupdate="cascade"),
    )


class claimsgroups(db.Model):
    __tablename__ = "claimsgroups"
    id = db.Column("id", db.Integer, primary_key=True)
    claimsid = db.Column(
        "claimsid",
        db.Integer,
        db.ForeignKey("claims.id", ondelete="cascade", onupdate="cascade"),
    )
    groupid = db.Column(
        "groupid",
        db.Integer,
        db.ForeignKey("groups.id", ondelete="cascade", onupdate="cascade"),
    )
