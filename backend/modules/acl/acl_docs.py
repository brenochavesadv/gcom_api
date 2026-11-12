roles_doc = {
    "list_roles": {
        'tags': ['Roles'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'order_by', 'in': 'query', 'type': 'string'},
            {'name': 'direction', 'in': 'query', 'type': 'string'},
            {'name': 'name', 'in': 'query', 'type': 'string'},
        ],
        'responses': {
            200: {
                'description': "Lista paginada de papéis"
            }
        }
    },
     "create_role": {
        'tags': ['Roles'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'permissions': {
                        'type': 'array',
                        'items': {'type': 'integer'}
                    }
                },
                'required': ['name']
            }
        }],
        'responses': {
            201: {'description': "Papel criado"}
        }
    },
}

permissions_doc = {
    "list_permissions": {
        'tags': ['Permissions'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'order_by', 'in': 'query', 'type': 'string'},
            {'name': 'direction', 'in': 'query', 'type': 'string'},
            {'name': 'name', 'in': 'query', 'type': 'string'},
        ],
        'responses': {
            200: {
                'description': "Lista paginada de permissões"
            }
        }
    },
     "create_permission": {
        'tags': ['Permissions'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'}
                },
                'required': ['name']
            }
        }],
        'responses': {
            201: {'description': "Permissão criada"}
        }
    },
}

role_permissions_doc = {
    "list_role_permissions": {
        'tags': ['Role Permissions'],
        'parameters': [
            {'name': 'page', 'in': 'query', 'type': 'integer'},
            {'name': 'per_page', 'in': 'query', 'type': 'integer'},
            {'name': 'order_by', 'in': 'query', 'type': 'string'},
            {'name': 'direction', 'in': 'query', 'type': 'string'},
            {'name': 'role_id', 'in': 'query', 'type': 'integer'},
        ],
        'responses': {
            200: {
                'description': "Lista paginada de permissões de papéis"
            }
        }
    },
    "create_role_permission": {
        'tags': ['Role Permissions'],
        'parameters': [{
            'name': 'body',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'role_id': {'type': 'integer'},
                    'permission_id': {'type': 'integer'}
                },
                'required': ['role_id', 'permission_id']
            }
        }],
        'responses': {
            201: {'description': "Permissão de papel criada"}
        }
    }
}