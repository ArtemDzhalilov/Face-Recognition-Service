import pydantic
import sqlalchemy
from sqlalchemy.orm import sessionmaker
from models import Users
class Database:

    def __init__(self, engine_args):
        self.engine = sqlalchemy.create_engine(
            engine_args,
        )
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
    @staticmethod
    def generate_random_api_key():
        return pydantic.UUID4().hex
    def create_ip_key(self, login, password):
        user = self.session.query(Users).filter(Users.login == login and Users.password == password).first()
        if user is None:
            return None
        else:
            user.api_key = self.generate_random_api_key()
            self.session.commit()
            return user
    def get_api_key(self, login, password):
        user = self.session.query(Users).filter(Users.login == login and Users.password == password).first()
        if user is None:
            return None
        else:
            return user.password
    def get_login_password(self, api_key):
        user = self.session.query(Users).filter(Users.api_key == api_key).first()
        if user is None:
            return None
        else:
            return user.login, user.password