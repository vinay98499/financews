import os
import json

class SecretsUtil:
    @staticmethod
    def get_token():
        # Try to load secrets.json from project root
        secrets_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'secrets.json')
        if not os.path.exists(secrets_path):
            # Try current directory
            secrets_path = os.path.join(os.path.dirname(__file__), 'secrets.json')
        if os.path.exists(secrets_path):
            with open(secrets_path, 'r') as f:
                secrets = json.load(f)
            return secrets.get('UPSTOX_ACCESS_TOKEN')
        return None
