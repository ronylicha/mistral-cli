// Fonction sans documentation
function processData(data) {
    var result = [];
    for (var i = 0; i < data.length; i++) {
        if (data[i] != null) {
            result.push(data[i].toUpperCase());
        }
    }
    return result;
}

// Fonction avec problèmes potentiels
function calculateTotal(prices) {
    var total = 0;
    for (var price of prices) {
        total += price; // Pas de validation du type
    }
    return total;
}

// Code principal
var items = ["apple", "banana", null, "cherry"];
var processed = processData(items);
console.log("Processed:", processed);

var prices = [10, 20, "30", 40]; // Erreur intentionnelle: string dans numbers
var total = calculateTotal(prices);
console.log("Total:", total);