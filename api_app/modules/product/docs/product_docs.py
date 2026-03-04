product_docs = {
    "create_product": {
        'tags': ['Product'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'instit_matriz_id_fk': {'type': 'integer'},
                    'codprod': {'type': 'integer'},
                    'ativo': {'type': 'integer'},
                    'descr': {'type': 'string'},
                    'descres': {'type': 'string'},
                    'und': {'type': 'integer'},
                    'prod_grp_id_fk': {'type': 'integer'},
                    'tam': {'type': 'number'}
                },
                'required': ['instit_matriz_id_fk', 'codprod', 'descr', 'und', 'prod_grp_id_fk', 'tam']
            }
        }],
        'responses': {
            201: {'description': 'Produto criado'}
        }
    },
}