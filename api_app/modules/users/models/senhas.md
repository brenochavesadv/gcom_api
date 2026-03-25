Para definir um campo de senha com hash SHA-256 no Flask-SQLAlchemy, não armazene senhas com SHA-256 puro, pois é inseguro.  Em vez disso, use bibliotecas projetadas para hashing de senhas, como bcrypt, passlib ou Flask-Security. 

✅ Método Recomendado: Usando Flask-Bcrypt
Instale o Flask-Bcrypt:
pip install Flask-Bcrypt

Configure no seu app:
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

Defina o modelo de usuário:
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)  # Armazena o hash

    def set_password(self, senha):
        self.password = bcrypt.generate_password_hash(senha).decode('utf-8')

    def check_password(self, senha):
        return bcrypt.check_password_hash(self.password, senha)

Uso ao registrar e logar:
# Registro
user = User(username="joao")
user.set_password("minha_senha")
db.session.add(user)
db.session.commit()

# Login
user = User.query.filter_by(username="joao").first()
if user and user.check_password("minha_senha"):
    print("Login bem-sucedido!")