from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class City(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "municipios"

    uid = db.Column('municipios_id', db.Integer, primary_key=True)
    name = db.Column('nome', db.String(50), nullable=False, comment='Name of the city')
    ibge_code = db.Column('cid_ibge', db.Integer, nullable=False, default=0, comment='IBGE code of the city')
    state_id_fk = db.Column('ufs_id_fk', db.Integer, nullable=False, default=0, comment='Foreign key to the state table')
    wikidata_id = db.Column(db.String(15), nullable=True, comment='Wikidata ID for the city')
    
    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid,
            'name': self.name,
            'ibge_code': self.ibge_code,
            'state_id_fk': self.state_id_fk,
            'wikidata_id': self.wikidata_id
        }
        return result
    
    def __repr__(self):
        return f"<City {self.uid} - {self.name}>"  
    def __str__(self):
        return f"City(uid={self.uid}, name={self.name}, ibge_code={self.ibge_code}, state_id_fk={self.state_id_fk})"
    