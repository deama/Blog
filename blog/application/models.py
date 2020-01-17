from application import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(player_id):
    return Account_details.query.get(int(player_id))


class Account_details(db.Model, UserMixin):
    player_id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    account_image_name = db.Column(db.String(255), nullable=False)

    id = player_id #satisfy UserMixin requirements

    blog = db.relationship("Blog", backref="account_details", lazy=True)

    def __repf__(self):
        return "".join([
                "login: ", self.login,
                "image_name:", self.account_image_name
            ])
            
class Blog(db.Model):
    blog_id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("account_details.player_id"))
    text = db.Column(db.String(1024), nullable=False)

    def __repf__(self):
        return "".join([
                "text: ", self.text
            ])

