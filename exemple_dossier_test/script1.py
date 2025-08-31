#!/usr/bin/env python3
def calculate_sum(a, b):
    # Fonction simple sans gestion d'erreurs
    return a + b

def process_list(items):
    # Code non optimisé
    result = []
    for i in range(len(items)):
        if items[i] > 0:
            result.append(items[i] * 2)
    return result

# Code principal sans documentation
if __name__ == "__main__":
    numbers = [1, -2, 3, 4, -5]
    doubled = process_list(numbers)
    print("Résultats:", doubled)
    
    total = calculate_sum(10, 20)
    print("Total:", total)