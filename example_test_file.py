#!/usr/bin/env python3
"""
Exemple de fichier Python pour tester l'analyseur de fichiers Mistral CLI.
Ce fichier contient quelques problèmes intentionnels pour démontrer les capacités d'analyse.
"""

import os
import sys
import json

def calculate_average(numbers):
    # Bug potentiel: pas de vérification de liste vide
    total = 0
    for num in numbers:
        total = total + num
    return total / len(numbers)

def read_config_file(filename):
    # Problème de sécurité: pas de validation du chemin
    with open(filename, 'r') as f:
        data = f.read()
    return json.loads(data)

class DataProcessor:
    def __init__(self):
        self.data = []
        
    def add_item(self, item):
        self.data.append(item)
    
    def process_data(self):
        # Problème de performance: code non optimisé
        result = []
        for i in range(len(self.data)):
            for j in range(len(self.data)):
                if i != j and self.data[i] == self.data[j]:
                    result.append(self.data[i])
        return result
    
    def save_to_file(self, filename):
        # Manque de gestion d'erreurs
        with open(filename, 'w') as f:
            json.dump(self.data, f)

if __name__ == "__main__":
    processor = DataProcessor()
    processor.add_item("test")
    processor.add_item("example")
    processor.add_item("test")  # Duplication intentionnelle
    
    result = processor.process_data()
    print("Résultat:", result)
    
    # Test de la fonction avec une liste vide (va provoquer une erreur)
    try:
        avg = calculate_average([1, 2, 3, 4, 5])
        print(f"Moyenne: {avg}")
    except Exception as e:
        print(f"Erreur: {e}")