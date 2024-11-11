from flask import Flask, request, jsonify
import ipaddress

app = Flask(__name__)

@app.route('/validate', methods=['GET'])
def validate_ip_and_mask():
    ip = request.args.get('ip')
    mask = request.args.get('mask')

    if not ip or not mask:
        return jsonify({"error": "Se requieren tanto la dirección IP como la máscara de red"}), 400

    try:
        # Intenta crear una red IPv4 con la IP y máscara proporcionadas
        network = ipaddress.IPv4Network(f"{ip}/{mask}", strict=False)
        
        return jsonify({
            "valid": True,
            "network": str(network.network_address),
            "broadcast": str(network.broadcast_address),
            "num_addresses": network.num_addresses,
            "netmask": str(network.netmask)
        })
    except ValueError as e:
        return jsonify({
            "valid": False,
            "error": str(e),
            "examples": [
                {"ip": "192.168.1.0", "mask": "24"},
                {"ip": "10.0.0.0", "mask": "8"},
                {"ip": "172.16.0.0", "mask": "16"}
            ]
        }), 400

@app.route('/examples', methods=['GET'])
def get_examples():
    return jsonify({
        "examples": [
            {"ip": "192.168.1.0", "mask": "24", "description": "Red de clase C típica para uso doméstico"},
            {"ip": "10.0.0.0", "mask": "8", "description": "Red de clase A para redes empresariales grandes"},
            {"ip": "172.16.0.0", "mask": "16", "description": "Red de clase B para redes empresariales medianas"},
            {"ip": "192.168.0.0", "mask": "16", "description": "Red más grande para uso doméstico o pequeñas empresas"},
            {"ip": "10.10.10.0", "mask": "28", "description": "Subred pequeña con 14 direcciones utilizables"}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)