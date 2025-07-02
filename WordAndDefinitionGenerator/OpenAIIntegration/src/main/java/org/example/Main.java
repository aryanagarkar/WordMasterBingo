package org.example;

public class Main {
    public static void main(String[] args) {
        String inputFilePath = "WordDefinitionsAndSynonyms.txt";
        String outputFilePath = "SynonymAndDefinitionCheckReport.txt";
        CheckDefinitionsAndSynonyms checker = new CheckDefinitionsAndSynonyms();
        checker.runCheck(inputFilePath, outputFilePath);
            
        // For now, just run image generation by default
        //System.out.println("🎨 Running Image Generator...");
        //ImageGenerator.generateImage("Perspective");
    }
}