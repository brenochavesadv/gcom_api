aliquota_docs = {
    "list_aliquotas": {
        'tags': ['Aliquotas'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'order_by', 'in': 'query', 'type': 'string'},
            {'name': 'direction', 'in': 'query', 'type': 'string'},
            {'name': 'descr', 'in': 'query', 'type': 'string'},
            {'name': 'bematech', 'in': 'query', 'type': 'string'},
        ],
        'responses': {
            200: {
                'description': 'Lista paginada de alíquotas'
            }
        }
    },
    "create_aliquota": {
        'tags': ['Aliquotas'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'instit_id_fk': {'type': 'integer'},
                    'descr': {'type': 'string'},
                    'bematech': {'type': 'string'},
                    'valor': {'type': 'number'}
                },
                'required': ['instit_id_fk', 'descr', 'bematech']
            }
        }],
        'responses': {
            201: {'description': 'Alíquota criada'}
        }
    }
}