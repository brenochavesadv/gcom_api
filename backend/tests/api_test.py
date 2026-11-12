from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def network_endpoint():
    with app.app_context():
        return jsonify({"message": "API is accessible from network!"})


def test_network_endpoint():
    with app.test_client() as client:
        response = client.get('/test')
    assert response.status_code == 200
    assert response.get_json()['message'] == 'API is accessible from network!'

if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    current_app.logger.debug(f"Local IP: {local_ip}")
    current_app.logger.debug(f"Access from network: http://{local_ip}:5000/test")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
