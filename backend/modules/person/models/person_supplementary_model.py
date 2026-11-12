from datetime import datetime
from backend.apps.commerciall_api.main import db
from sqlalchemy.orm import relationship

class PersonSupplementary(db.Model):
    __bind_key__ = 'DB_MAIN' 
    __tablename__ = "person_supplementary"

    person_uid_fk = db.Column(db.String(36), db.ForeignKey('pescod.pescod_id'), primary_key=True)
    father_name = db.Column(db.String(100))
    mother_name = db.Column(db.String(100))
    profession = db.Column(db.String(40))
    professional_id = db.Column(db.String(15))
    salary = db.Column(db.Numeric)
    employer = db.Column(db.String(100))
    employer_contact = db.Column(db.String(100))
    cnpj = db.Column(db.String(25))
    iest = db.Column(db.String(15))
    imun = db.Column(db.String(15))
    emprend = db.Column(db.String(60), nullable=True)
    other_incomes = db.Column(db.String(60))
    incomes_sum = db.Column(db.Numeric)
    file_income_tax = db.Column(db.Integer)
    marital_status = db.Column(db.Integer)
    children = db.Column(db.Integer)
    alimony = db.Column(db.Numeric)
    spouse = db.Column(db.String(100))
    spouse_id_card = db.Column(db.String(25))
    spouse_profession = db.Column(db.String(40))
    spouse_employer = db.Column(db.String(100))
    spouse_incomes = db.Column(db.Numeric)
    spouse_phone = db.Column(db.String(15))
    spouse_email = db.Column(db.String(40))
    sync_status = db.Column(db.String(10), nullable=False, default='PENDING', comment='PENDING:not synced SYNCED:synced')
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=db.func.now())
    
    person = relationship("Person", back_populates="supplementary", lazy='select', foreign_keys=[person_uid_fk])

    def to_dict(self):
        """Convert model to dictionary using direct attribute access"""
        return {
            'person_uid_fk': self.person_uid_fk if self.person_uid_fk is not None else 0,
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
            'sync_status': self.sync_status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    

    # FACTORY FOR PERSON_NATURAL
    @staticmethod
    def from_json(data):
        return PersonSupplementary(
            person_uid_fk=data.get("person_uid_fk"),
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
            spouse_email=data.get("spouse_email"),
            sync_status=data.get("sync_status"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    
    
