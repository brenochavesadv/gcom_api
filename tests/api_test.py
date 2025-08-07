from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"message": "API is accessible from network!"})

if __name__ == '__main__':
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print(f"Local IP: {local_ip}")
    print(f"Access from network: http://{local_ip}:5000/test")
    
    app.run(host='0.0.0.0', port=5000, debug=True)