from main import db

class SyncQueue(db.Model):
  # __bind_key__ = 'main'  # SQLAlchemy to use the 'main' bind
    __tablename__ = "sync_queue"

    id = db.Column(db.Integer, primary_key=True)
    organization_uid_fk = db.Column(db.String(36), db.ForeignKey('instit.uid'))
    operation_type = db.Column(db.String(7), nullable=False)  # e.g., 'create', 'update', 'delete'
    operation_table = db.Column(db.String(30), nullable=False)  # e.g., 'users', 'organization'
    operation_uid = db.Column(db.String(36), nullable=False)  # UID of the record being operated on
    operation_date = db.Column(db.DateTime, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'organization_uid_fk': self.organization_uid_fk,
            'operation_type': self.operation_type,
            'operation_table': self.operation_table,
            'operation_uid': self.operation_uid,
            'operation_date': self.operation_date.isoformat() if self.operation_date else None
        }
