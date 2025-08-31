import os

def read_file(filename):
    # Problème de sécurité: pas de validation du chemin
    with open(filename, 'r') as f:
        return f.read()

def save_data(data, filename):
    # Pas de gestion d'erreurs
    with open(filename, 'w') as f:
        f.write(data)

class DataManager:
    def __init__(self):
        self.data = []
    
    def add_item(self, item):
        self.data.append(item)
    
    def get_items(self):
        return self.data