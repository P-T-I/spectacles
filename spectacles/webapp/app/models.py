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
    avatar_s = db.Column(db.String(64))
    avatar_m = db.Column(db.String(64))
    avatar_l = db.Column(db.String(64))

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
            filenames = avatar.generate(text=self.name)
            self.avatar_s = filenames[0]
            self.avatar_m = filenames[1]
            self.avatar_l = filenames[2]
            db.session.commit()
        except FileNotFoundError:
            pass
