
# Funções para buscar dados da FIPE API (Parallelum) e salvar no banco local

from datetime import datetime, timedelta

from main import db
from ..models.fipe_models import FipeBrand, FipeSyncControl, FipeVehycle
from ..models.vehycle_models import VehyclesTypes

import requests
import uuid

BASE_URL = "https://fipe.parallelum.com.br/api/v2"
headers = {
	'Accept': 'application/json',
	'Content-Type': 'application/json'
}

###
### BRANDS
###

def fetch_fipe_brands(vehicle_type: VehyclesTypes):
	"""Busca marcas da FIPE para o tipo de veículo especificado."""
	url = f"{BASE_URL}/{vehicle_type.value}/brands"
	try:
		response = requests.get(url,headers=headers)
		response.raise_for_status()
		data = response.json()

		return data

	except requests.RequestException as e:
		raise e  # Pode ser logado ou tratado de forma mais específica conforme necessário

def update_all_fipe_brands():
	"""Busca e armazena marcas da FIPE no banco local."""
	last_update = FipeSyncControl.query.order_by(FipeSyncControl.brands_last_update_at.desc()).first()
 
	update_fipe_brands = True
	if last_update:
		# check if last update was more than 48 hours ago
		time_diff = datetime.now() - last_update.brands_last_update_at
		update_fipe_brands = time_diff >= timedelta(days=20)

	data = []
 
	try:
		if update_fipe_brands:
			for vtype in VehyclesTypes:

				brands_data = fetch_fipe_brands(vtype)

		
				for brand in brands_data:
					# Verifica se já existe
					existing = FipeBrand.query.filter_by(fipe_code=brand['code'], type=vtype.value).first()
					if not existing:
						new_brand = FipeBrand(
							uid=str(uuid.uuid4()),
							fipe_code=brand['code'],
							name=brand['name'],
							type=vtype.value,
						)
						db.session.add(new_brand)
					else:
						existing.name = brand['name']
						db.session.add(existing)

				db.session.commit()
				updated = FipeSyncControl(
					uid=str(uuid.uuid4()),
					brands_last_update_at = datetime.now(),
					type = vtype.value,
				)
		
				db.session.add(updated)
				db.session.commit()

		brands = FipeBrand.query.all()
		data = [brand.to_dict() for brand in brands]

		return data

	except Exception as e:
		db.session.rollback()
		raise e 

###
### VEHYCLES
###

def fetch_fipe_vehycles(vehicle_type: VehyclesTypes , brand_code: str):
	"""Busca veículos da FIPE para o tipo de veículo especificado."""
	url = f"{BASE_URL}/{vehicle_type.value}/brands/{brand_code}/models"
	response = requests.get(url)
	response.raise_for_status()

	return response.json()

def fetch_fipe_years_by_model(vehycle_type: str , brand_code: str, vehycle_code: str):
	"""Busca veículos da FIPE para o tipo de veículo especificado."""

	url = f"{BASE_URL}/{vehycle_type}/brands/{brand_code}/models/{vehycle_code}/years"

	response = requests.get(url)
	response.raise_for_status()
	years_data = response.json()

	_yearsStringList = ''

	for year in years_data:
		_yearsStringList += f"{year.get('code')},{year.get('name')};"

	_vehycle = FipeVehycle.query.filter_by(
		fipe_code=vehycle_code,
		fipe_brand_code_fk=brand_code,
		type=vehycle_type,
	).first()

	if _vehycle is not None:
		_vehycle.model_years = _yearsStringList

		db.session.add(_vehycle)
		db.session.commit()
 
		return _vehycle.to_dict()

	return None

def update_fipe_vehycles_from_brand(brand_code: str , vehicle_type: VehyclesTypes):
	"""Busca e armazena veículos da FIPE no banco local."""
	vehycles_data = fetch_fipe_vehycles(vehicle_type, brand_code)

	vehycle_models = vehycles_data.get('models', []) if isinstance(vehycles_data, dict) else vehycles_data

	result = []

	for vehycle in vehycle_models:
		_code = vehycle.get('code')

		try:

			_vehycle = FipeVehycle.query.filter_by(
					fipe_code=_code,
					fipe_brand_code_fk=brand_code,
					type=vehicle_type.value,
				).first()

			if not _vehycle:
					new_vehycle = FipeVehycle(
						uid=str(uuid.uuid4()),
						fipe_code=_code,
						name=vehycle.get('name'),
						model_years=None,
						fipe_brand_code_fk=brand_code,
						type=vehicle_type.value,
					)
					db.session.add(new_vehycle)
					result.append({
						'uid': new_vehycle.uid,
						'fipe_code': new_vehycle.fipe_code,
						'name': new_vehycle.name,
						'fipe_brand_code_fk': new_vehycle.fipe_brand_code_fk,
						'type': new_vehycle.type,
						'years': None,
					})
			else:
				_vehycle.name = vehycle.get('name')
				_vehycle.type = vehicle_type.value
				db.session.add(_vehycle)

				result.append({
					'uid': _vehycle.uid,
					'fipe_code': _vehycle.fipe_code,
					'name': _vehycle.name,
					'fipe_brand_code_fk': _vehycle.fipe_brand_code_fk,
					'type': _vehycle.type,
					'years': None,
				})

		except Exception as e:
			raise Exception(f"Error saving vehicle with code {_code} and brand {brand_code}: {e}")

	fipe_update = FipeSyncControl(
		uid=str(uuid.uuid4()),
		type=vehicle_type.value,
		vehycle_brand=brand_code,
		vehycle_brand_last_update_at=datetime.now()
        )
 
	db.session.add(fipe_update)
	db.session.commit()

	return result

def update_all_fipe_vehycles():
	"""Atualiza todos os veículos de carros, motos e caminhões da FIPE no banco local."""
	data = []
	for vtype in VehyclesTypes:
		brands = FipeBrand.query.filter_by(type=vtype).all()
		for brand in brands:
			items = update_fipe_vehycles_from_brand(brand.fipe_code, vtype)
			if items:
				data.extend(items)
	return data