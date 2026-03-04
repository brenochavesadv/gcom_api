person_natural_docs = {
    "list_person_natural": {
        'tags': ['Person Natural'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'sort', 'in': 'query', 'type': 'string'},
            {'name': 'name', 'in': 'query', 'type': 'string'},
            {'name': 'id_number', 'in': 'query', 'type': 'string'},
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
    "create_person_natural": {
        'tags': ['Person Natural'],
         'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                
            }
        }],
        'responses': {
            201: {
                'description': 'Pessoa natural criada com sucesso'
            }
        }
    },
    "update_person_natural": {
        'tags': ['Person Natural'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',

            }
        }],
        'responses': {
            200: {
                'description': 'Pessoa natural atualizada com sucesso'
            }
        }
    }
}