package org.example;

/**
 * Entry point for the Word and Definition Generator application.
 *
 * Workflow:
 * 1. Reads a list of words from src/main/resources/WordsToProcess.txt.
 * 2. For each word, generates a definition and three synonyms (easy, medium, hard) using OpenAI.
 * 3. Writes the results to WordDefinitionsAndSynonyms.txt.
 * 4. Runs the CheckDefinitionsAndSynonyms checker on the generated file to produce a detailed report and improved word list.
 */

public class Main {
    /**
     * Main method to automate the process of generating definitions/synonyms and checking them.
     * @param args Command-line arguments (not used).
     */
    public static void main(String[] args) {
        // Step 1: Read the list of words to process.
        String wordsFilePath = "src/main/resources/WordsToProcess.txt";
        String outputFilePath = "WordDefinitionsAndSynonyms.txt";
        java.util.List<String> words = new java.util.ArrayList<>();
        try (java.io.BufferedReader reader = new java.io.BufferedReader(new java.io.FileReader(wordsFilePath))) {
            String line;
            while ((line = reader.readLine()) != null) {
                if (!line.trim().isEmpty()) {
                    words.add(line.trim());
                }
            }
        } catch (java.io.IOException e) {
            System.err.println("Error reading words file: " + e.getMessage());
            return;
        }

        // Step 2: Generate definitions and synonyms for each word.
        java.util.List<String> outputLines = new java.util.ArrayList<>();
        for (String word : words) {
            // Get definition and synonyms for the word using OpenAI.
            String defAndSyns = MeaningAndSynonymFetcher.getDefinitions(word);
            if (defAndSyns != null && !defAndSyns.isEmpty()) {
                // Add the result to the output list in the required format.
                outputLines.add(word + ": " + defAndSyns);
            } else {
                // If no result, write that in the output.
                outputLines.add(word + ": (No definition/synonyms found)");
            }
        }

        // Step 3: Write the generated definitions and synonyms to the output file.
        try (java.io.BufferedWriter writer = new java.io.BufferedWriter(new java.io.FileWriter(outputFilePath))) {
            for (String line : outputLines) {
                writer.write(line);
                writer.write("\n");
            }
            System.out.println("Word definitions and synonyms written to: " + outputFilePath);
        } catch (java.io.IOException e) {
            System.err.println("Error writing output file: " + e.getMessage());
        }

        // Step 4: Run the checker to validate and refine the generated file.
        String reportFilePath = "SynonymAndDefinitionCheckReport.txt";
        CheckDefinitionsAndSynonyms checker = new CheckDefinitionsAndSynonyms();
        checker.runCheck(outputFilePath, reportFilePath);
    }
}