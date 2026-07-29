from datetime import datetime
from pytz import UTC
from main import db
from sqlalchemy.orm import relationship

class PersonNatural(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "pesfis"

    uid = db.Column("pesfis_id", db.Integer, primary_key=True)
    person_uid_fk = db.Column("pescod_id_fk", db.Integer, db.ForeignKey('pescod.pescod_id'))
    id_card = db.Column("identidade", db.String(25)) 
    id_issuer = db.Column("emissor_identidade", db.String(15))
    birth_date = db.Column("data_de_nascimento", db.Date)
    birth_city = db.Column(db.String(80))
    pronoun = db.Column("tratam", db.Integer)
    nickname = db.Column("apelido", db.String(30))
    gender = db.Column("sexo", db.Integer)
    father_name = db.Column("pai", db.String(100))
    mother_name = db.Column("mae", db.String(100))
    profession = db.Column("profissao", db.String(40))
    professional_id = db.Column("ctps", db.String(10))
    salary = db.Column("salario", db.Numeric)
    employer = db.Column("empresa", db.String(100))
    employer_contact = db.Column("resp", db.String(100))
    cnpj = db.Column("cnpj", db.String(25))
    iest = db.Column("iest", db.String(15))
    imun = db.Column("imun", db.String(15))
    emprend = db.Column("emprend", db.String(60), nullable=True)
    other_incomes = db.Column("orendas", db.String(60))
    incomes_sum = db.Column("vrendas", db.Numeric)
    file_income_tax = db.Column("irpf", db.Integer)
    marital_status = db.Column("estcivil", db.Integer)
    children = db.Column("depend", db.Integer)
    alimony = db.Column("pensao", db.Numeric)
    spouse = db.Column("conjuge", db.String(100))
    spouse_id_card = db.Column("cpfconj", db.String(25))
    spouse_profession = db.Column("profconj", db.String(40))
    spouse_employer = db.Column("emprconj", db.String(100))
    spouse_incomes = db.Column("rendaconj", db.Numeric)
    spouse_phone = db.Column("telconj", db.String(15))
    spouse_email = db.Column("mailconj", db.String(40))
    person = relationship("Person", back_populates="person_natural", foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        result = {
            'uid': self.uid if self.uid is not None else 0,
            'person_uid_fk': self.person_uid_fk if self.person_uid_fk is not None else 0,
            'id_card': self.id_card if self.id_card is not None else "",
            'id_issuer': self.id_issuer if self.id_issuer is not None else "",
            'birth_date': str(self.birth_date) if self.birth_date is not None else "",
            'birth_city': self.birth_city if self.birth_city is not None else "",
            'pronoun': self.pronoun if self.pronoun is not None else 0,
            'nickname': self.nickname if self.nickname is not None else "",
            'gender': self.gender if self.gender is not None else 0,
            'father_name': self.father_name if self.father_name is not None else "",
            'mother_name': self.mother_name if self.mother_name is not None else "",
            'profession': self.profession if self.profession is not None else "",
            'professional_id': self.professional_id if self.professional_id is not None else "",
            'salary': float(self.salary) if self.salary is not None else 0,
            'employer': self.employer if self.employer is not None else "",
            'employer_contact': self.employer_contact if self.employer_contact is not None else "",
            'cnpj': self.cnpj if self.cnpj is not None else "",
            'iest': self.iest if self.iest is not None else "",
            'imun': self.imun if self.imun is not None else "",
            'emprend': self.emprend if self.emprend is not None else "",
            'other_incomes': self.other_incomes if self.other_incomes is not None else "",
            'incomes_sum': float(self.incomes_sum) if self.incomes_sum is not None else 0,
            'file_income_tax': self.file_income_tax if self.file_income_tax is not None else 0,
            'marital_status': self.marital_status if self.marital_status is not None else 0,
            'children': self.children if self.children is not None else 0,
            'alimony': float(self.alimony) if self.alimony is not None else 0,
            'spouse': self.spouse if self.spouse is not None else "",
            'spouse_id_card': self.spouse_id_card if self.spouse_id_card is not None else "",
            'spouse_profession': self.spouse_profession if self.spouse_profession is not None else "",
            'spouse_employer': self.spouse_employer if self.spouse_employer is not None else "",
            'spouse_incomes': float(self.spouse_incomes) if self.spouse_incomes is not None else 0,
            'spouse_phone': self.spouse_phone if self.spouse_phone is not None else "",
            'spouse_email': self.spouse_email if self.spouse_email is not None else "",
        }
        return result

    def update_from(self, other):
        """Update mutable fields from another PersonNatural-like object.

        `other` can be a PersonNatural instance or an object with compatible attributes.
        Only updates fields that are safe to change (no PK/FK).
        """
        updatable_fields = [
            "id_card",
            "id_issuer",
            "birth_date",
            "birth_city",
            "pronoun",
            "nickname",
            "gender",
            "father_name",
            "mother_name",
            "profession",
            "professional_id",
            "salary",
            "employer",
            "employer_contact",
            "cnpj",
            "iest",
            "imun",
            "emprend",
            "other_incomes",
            "incomes_sum",
            "file_income_tax",
            "marital_status",
            "children",
            "alimony",
            "spouse",
            "spouse_id_card",
            "spouse_profession",
            "spouse_employer",
            "spouse_incomes",
            "spouse_phone",
            "spouse_email",
        ]
        for field in updatable_fields:
            if hasattr(other, field):
                setattr(self, field, getattr(other, field))
        
    # FACTORY FOR PERSON_NATURAL
    @staticmethod
    def from_json(data):
        person_natural = PersonNatural(
            id_card=data.get("id_card"),
            id_issuer=data.get("id_issuer"),
            birth_date=data.get("birth_date"),
            birth_city=data.get("birth_city"),
            pronoun=data.get("pronoun"),
            nickname=data.get("nickname"),
            gender=data.get("gender"),
            father_name=data.get("father_name"),
            mother_name=data.get("mother_name"),
            profession=data.get("profession"),
            professional_id=data.get("professional_id"),
            salary=data.get("salary") if data.get("salary") is not None else 0,
            employer=data.get("employer"),
            employer_contact=data.get("employer_contact"),
            other_incomes=data.get("other_incomes"),
            incomes_sum=data.get("incomes_sum"),
            file_income_tax=data.get("file_income_tax"),
            marital_status=data.get("marital_status"),
            children=data.get("children"),
            alimony=data.get("alimony"),
            spouse=data.get("spouse"),
            spouse_id_card=data.get("spouse_id_card"),
            spouse_profession=data.get("spouse_profession"),
            spouse_employer=data.get("spouse_employer"),
            spouse_incomes=data.get("spouse_incomes"),
            spouse_phone=data.get("spouse_phone"),
            spouse_email=data.get("spouse_email")
        )
        return person_natural
    
    
