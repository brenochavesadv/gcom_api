from api_app import create_app, db
from api_app.modules.auth.auth_user_model import AuthUser
from api_app.modules.product.models.product_tax_info_br_model import Aliquota
from api_app.modules.product.models.product_model import Produtos
from passlib.hash import bcrypt

app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()

    user = AuthUser(username="admin", email="admin@example.com", hashed_password=bcrypt.hash("admin123"))
    db.session.add(user)

    db.session.add_all([
        Aliquota(instit_id_fk=1, descr="A1", bematech="01", valor=5.00),
        Aliquota(instit_id_fk=1, descr="B2", bematech="02", valor=10.00)
    ])

    db.session.add_all([
        Produtos(instit_matriz_id_fk=1, codprod=1001, descr="Produto A", und=1, prod_grp_id_fk=1, tam=1.000),
        Produtos(instit_matriz_id_fk=1, codprod=1002, descr="Produto B", und=1, prod_grp_id_fk=1, tam=2.500)
    ])

    db.session.commit()
    print("Seed concluído com sucesso.")