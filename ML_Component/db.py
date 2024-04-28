from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DB:
    def __init__(self, url):
        engine = create_engine(url)
        Session = sessionmaker(bind=engine)
        self.session = Session()
    def get_all_owners(self, device, device_name):
        return self.session.query(device.owner).filter(device.name == device_name)

    def get_all_faces(self, Faces, all_owners):
        return self.session.query(Faces).filter(Faces.owner.in_(all_owners)).all()
