from flask import Blueprint, current_app
import re

health_bp = Blueprint('health', __name__)


def _mask_db_uri(uri: str) -> str:
    if not uri:
        return ""
    # Mask password between ':' and '@' in the authority portion
    return re.sub(r"(://[^:/]+:)([^@]+)(@)", r"\1***\3", uri)


@health_bp.route('/test', methods=['GET'])
def health_check():
    """Check if the server is online and return a masked DB URI for debugging."""
    uri = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    masked = _mask_db_uri(uri) if uri else None
    return {
        'status': 'online',
        'db_uri': masked,
        'message': 'Server is running'
    }, 200