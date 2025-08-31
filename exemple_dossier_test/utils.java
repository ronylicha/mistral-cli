public class Utils {
    
    // Méthode sans gestion d'erreurs
    public static int divide(int a, int b) {
        return a / b; // Division par zéro possible
    }
    
    // Méthode non optimisée
    public static String processString(String input) {
        String result = "";
        for (int i = 0; i < input.length(); i++) {
            result += input.charAt(i); // Inefficient string concatenation
        }
        return result.toUpperCase();
    }
    
    // Méthode avec logique simple
    public static boolean isValid(String value) {
        if (value == null) return false;
        return value.length() > 0;
    }
    
    public static void main(String[] args) {
        System.out.println(divide(10, 2));
        System.out.println(processString("hello"));
        System.out.println(isValid("test"));
    }
}