person_docs = {
    "list_person": {
        'tags': ['Person'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'sort', 'in': 'query', 'type': 'string'},
            {'name': 'name', 'in': 'query', 'type': 'string'},
            {'name': 'cpf', 'in': 'query', 'type': 'string'},
            {'name': 'uid', 'in': 'query', 'type': 'integer'},
            {'name': 'is_active', 'in': 'query', 'type': 'boolean'},
            {'name': 'is_supplier', 'in': 'query', 'type': 'boolean'},
            {'name': 'type', 'in': 'query', 'type': 'string'},
            {'name': 'organization_uid', 'in': 'query', 'type': 'integer'}
        ],
        'responses': {
            200: {
                'description': 'Lista paginada de Pessoas'
            }
        }
    },
    "list_person_natural": {
        'tags': ['Person Natural'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'sort', 'in': 'query', 'type': 'string'},
            {'name': 'name', 'in': 'query', 'type': 'string'},
            {'name': 'cpf', 'in': 'query', 'type': 'string'},
            {'name': 'uid', 'in': 'query', 'type': 'integer'},
            {'name': 'is_active', 'in': 'query', 'type': 'boolean'},
            {'name': 'is_supplier', 'in': 'query', 'type': 'boolean'},
            {'name': 'type', 'in': 'query', 'type': 'string'},
            {'name': 'organization_uid', 'in': 'query', 'type': 'integer'}
        ],
        'responses': {
            200: {
                'description': 'Lista paginada de Pessoas'
            }
        }
    },
 

}