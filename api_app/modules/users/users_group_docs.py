users_group_docs = {
    "list_users_group": {
        'tags': ['Users Group'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
        ],
        'responses': {
            200: {
                'description': 'Lista paginada de Grupos de Usuários'
            }
        }
    },
    "create_users_group": {
        'tags': ['Users Group'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'description': {'type': 'string'}
                },
                'required': ['name']
            }
        }],
        'responses': {
            200: {
                'description': 'Grupo de Usuários criado',
            }
        }
    },
    "update_users_group": {
        'tags': ['Users Group'],
        'parameters': [
            {'name': 'uid', 'in': 'path', 'type': 'integer', 'required': True},
            {
                'name': 'body',
                'in': 'body',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'description': {'type': 'string'}
                    },
                    'required': ['name']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Grupo de Usuários atualizado'
            }
        }
    },
    "delete_users_group": {
        'tags': ['Users Group'],
        'parameters': [
            {'name': 'uid', 'in': 'path', 'type': 'integer', 'required': True}
        ],
        'responses': {
            200: {
                'description': 'Grupo de Usuários excluído'
            }
        }
    },
    "get_users_group": {
        'tags': ['Users Group'],
        'parameters': [
            {'name': 'uid', 'in': 'path', 'type': 'integer', 'required': True}
        ],
        'responses': {
            200: {
                'description': 'Detalhes do Grupo de Usuários'
            }
        }
    }
}