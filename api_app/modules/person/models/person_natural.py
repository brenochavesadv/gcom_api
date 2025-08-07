from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class PersonNatural(db.Model):
    __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "pesfis"

    id = db.Column("pesfis_id", db.Integer, primary_key=True)
    person_control_id_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    id_card = db.Column("identidade", db.String, primary_key=False)
    id_issuer = db.Column("emissor_identidade", db.String, primary_key=False)
    birth_city = db.Column("naturalidade_id_fk", db.Integer, primary_key=False)
    birth_date = db.Column("data_de_nascimento", db.String, primary_key=False)
    pronoum_id_fk = db.Column("tratam", db.Integer, primary_key=False)
    nickname = db.Column("apelido", db.String, primary_key=False)
    gender = db.Column("sexo", db.Integer, primary_key=False)
    father_name = db.Column("pai", db.String, primary_key=False)
    mother_name = db.Column("mae", db.String, primary_key=False)
    profession = db.Column("profissao", db.String, primary_key=False)
    ctps = db.Column("ctps", db.String, primary_key=False)
    salary = db.Column("salario", db.Numeric, primary_key=False)
    company = db.Column("empresa", db.String, primary_key=False)
    resp = db.Column("resp", db.String, primary_key=False)
    cnpj = db.Column("cnpj", db.String, primary_key=False)
    iest = db.Column("iest", db.String, primary_key=False)
    imun = db.Column("imun", db.String, primary_key=False)
    emprend = db.Column("emprend", db.String, primary_key=False)
    orendas = db.Column("orendas", db.String, primary_key=False)
    vrendas = db.Column("vrendas", db.Numeric, primary_key=False)
    irpf = db.Column("irpf", db.Integer, primary_key=False)
    estcivil = db.Column("estcivil", db.Integer, primary_key=False)
    depend = db.Column("depend", db.Integer, primary_key=False)
    pensao = db.Column("pensao", db.Numeric, primary_key=False)
    spouse = db.Column("conjuge", db.String, primary_key=False)
    cpfconj = db.Column("cpfconj", db.String, primary_key=False)
    profconj = db.Column("profconj", db.String, primary_key=False)
    emprconj = db.Column("emprconj", db.String, primary_key=False)
    rendaconj = db.Column("rendaconj", db.Numeric, primary_key=False)
    telconj = db.Column("telconj", db.String, primary_key=False)
    mailconj = db.Column("mailconj", db.String, primary_key=False)

    # Add the missing relationship
    person_control = relationship("PersonControl", back_populates="person_natural")

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'id': self.id,
            'person_control_id_fk': self.person_control_id_fk,
            'id_card': self.id_card,
            'id_issuer': self.id_issuer,
            'birth_city': self.birth_city,
            'birth_date': str(self.birth_date),
            'pronoum_id_fk': self.pronoum_id_fk,
            'nickname': self.nickname,
            'gender': self.gender,
            'father_name': self.father_name,
            'mother_name': self.mother_name,
            'profession': self.profession,
            'ctps': self.ctps,
            'salary': float(self.salary) if self.salary is not None else None,
            'company': self.company,
            'resp': self.resp,
            'cnpj': self.cnpj,
            'iest': self.iest,
            'imun': self.imun,
            'emprend': self.emprend,
            'orendas': self.orendas,
            'vrendas': float(self.vrendas) if self.vrendas is not None else None,
            'irpf': self.irpf,
            'estcivil': self.estcivil,
            'depend': self.depend,
            'pensao': float(self.pensao) if self.pensao is not None else None,
            'spouse': self.spouse,
            'cpfconj': self.cpfconj,
            'profconj': self.profconj,
            'emprconj': self.emprconj,
            'rendaconj': float(self.rendaconj) if self.rendaconj is not None else None,
            'telconj': self.telconj,
            'mailconj': self.mailconj,

        }
        return result

    def __repr__(self):
        return f"<PersonNatural {self.id} - {self.person_control_id_fk}>"

    def __str__(self):
        return f"PersonNatural(id={self.id}, nickname={self.nickname}, person_control_id_fk={self.person_control_id_fk})"