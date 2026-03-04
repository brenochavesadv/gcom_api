users_docs = {
    "list_users": {
        'tags': ['Users'],
        'parameters': [
            {'name': 'uid', 'in': 'query', 'type': 'integer'},
            {'name': 'uid', 'in': 'query', 'type': 'string'},
            {'name': 'organization_uid', 'in': 'query', 'type': 'integer'},
            {'name': 'name', 'in': 'query', 'type': 'string'},
            {'name': 'group_id', 'in': 'query', 'type': 'integer'},
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
        ],
        'responses': {
            200: {
                'description': 'Lista paginada de Usuários'
            }
        }
    },
}