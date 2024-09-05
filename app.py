import requests
import json
import logging
from flask import Flask, request, Response, jsonify
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*",
            "allow_headers": "*"}}, allow_headers=['Content-Type', 'Authorization'])
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/proxy/api/projects', methods=['POST'])
def proxy_api():
    # Get the JSON data from the request
    order_data = request.get_json()
    if not order_data:
        logging.info('Error: No data provided')
        return jsonify({'error': 'No data provided'}), 400
    try:
        result = update_projects(order_data)
        if result:
            logging.info(f'Success: {result}')
            return result
        logging.info('Success: Projects successfully matched')
        return jsonify({'success': True, 'message': 'Projects successfully matched'}), 200
    
    except Exception as e:
        # Log the error but return a 200 status code to shopify
        logging.error(f"Error processing order: {str(e)}")
        return jsonify({'error': 'An error occurred while processing the order'}), 200


def update_projects(order_clever):
    user_id = order_clever['customer']['id']
    print(user_id)
    
    line_items = order_clever.get('line_items', [])
    
    for item in line_items:
        properties = item.get('properties', [])
        
        for prop in properties:
            if prop['name'] == "Project ID":
                project_id = prop['value']
                
                url = f"https://cleverfaces-api.ddns.net/api/projects/{project_id}"
                print(f"Requesting URL: {url}")

                payload = json.dumps({
                    "user_id": str(user_id)
                })
                headers = {
                    'Content-Type': 'application/json'
                }


                print(f"Payload: {payload}")
                try:
                    response = requests.request("PUT", url, headers=headers, data=payload)                    
                    print(f"Response status code: {response.status_code}")
                    print(f"Response content: {response.text}")
                    
                    # Gérer la réponse de l'API
                    if response.status_code == 200:
                        try:
                            json_response = response.json()
                            print(f"JSON Response: {json_response}")
                            print(f"Project ID {project_id} mis à jour avec succès pour l'utilisateur {user_id}.")
                            return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
                        except json.JSONDecodeError:
                            print(f"La réponse n'est pas un JSON valide: {response.text}")
                    else:
                        print(f"Erreur lors de la mise à jour du projet {project_id}: {response.status_code} - {response.text}")
                except requests.RequestException as e:
                    print(f"Erreur de requête pour le projet {project_id}: {str(e)}")   