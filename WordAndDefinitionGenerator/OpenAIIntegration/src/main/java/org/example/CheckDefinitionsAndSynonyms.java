package org.example;

import java.io.*;
import java.util.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * This class processes a file containing words, their definitions, and synonyms, and checks the accuracy and appropriateness
 * of the definitions and synonyms using OpenAI. It creates files containing a detailed report and a new word list with improved definitions
 * and synonyms to ensure they are accurate and grade-appropriate (easy - grades 1 to 5, medium - grades 6 to 8, hard - grades 9 to 12).
 */

public class CheckDefinitionsAndSynonyms {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // Reference examples for grade-appropriate vocabulary difficulty.
    private static final String GRADE_REFERENCE_1_5 = "words like 'forgiveness', 'upset', and 'disaster' are appropriate for grades 1-5";
    private static final String GRADE_REFERENCE_6_8 = "'absolution', 'resilient', and 'debacle' are appropriate for grades 6-8";
    private static final String GRADE_REFERENCE_9_12 = "'obsequious', 'ubiquitous', and 'conundrum' are appropriate for grades 9-12";

    /**
     * Processes the input file, checks and refines definitions and synonyms, and writes a report and improved word list to files.
     * @param inputFilePath Path to the input file containing words, definitions, and synonyms.
     * @param outputFilePath Path to the output file for the report.
     */
    public void runCheck(String inputFilePath, String outputFilePath) {
        // Check if input file exists.
        if (!new File(inputFilePath).exists()) {
            System.err.println("Error: Input file not found: " + inputFilePath);
            return;
        }
        
        List<String> report = new ArrayList<>();
        List<String> improvedWordLines = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFilePath))) {
            String line;
            int lineNumber = 0;
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                if (line.trim().isEmpty()) continue;
                
                try {
                    // Split the line into word and definition/synonyms part.
                    String[] parts = line.split(": ", 2);
                    if (parts.length != 2) {
                        System.err.println("Warning: Skipping malformed line " + lineNumber + ": " + line);
                        continue;
                    }
                    
                    String word = parts[0].trim();
                    // Split the definition and synonyms.
                    String[] defAndSyns = parts[1].split(",");
                    if (defAndSyns.length < 4) {
                        System.err.println("Warning: Skipping line " + lineNumber + " - insufficient synonyms: " + line);
                        continue;
                    }
                    
                    // Iteratively improve definition.
                    String definition = refineDefinition(word, defAndSyns[0].trim(), 3);
                    
                    // Iteratively improve synonyms for each difficulty level.
                    String easy = refineSynonym(word, definition, defAndSyns[1].trim(), 1, 5, 3);
                    String medium = refineSynonym(word, definition, defAndSyns[2].trim(), 6, 8, 3);
                    String hard = refineSynonym(word, definition, defAndSyns[3].trim(), 9, 12, 3);

                    // Generate a report entry and add to the report list.
                    String reportEntry = generateReportEntry(word, definition, easy, medium, hard);
                    report.add(reportEntry);

                    // Add improved word line for output file.
                    improvedWordLines.add(
                        String.format("%s: %s, %s, %s, %s", word, definition, easy, medium, hard)
                    );
                    
                } catch (Exception e) {
                    System.err.println("Error processing line " + lineNumber + ": " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            return;
        }

        // Write the report to the output file.
        writeReportToFile(report, outputFilePath);

        // Write the improved words to a new file.
        String improvedWordsFilePath = "WordDefinitionsAndSynonyms_Improved.txt";
        writeImprovedWordsFile(improvedWordLines, improvedWordsFilePath);
    }

    /**
     * Generates a formatted report entry for a word, including definition and synonym checks.
     * @param word The word being checked.
     * @param definition The refined definition.
     * @param easy The easy-level synonym.
     * @param medium The medium-level synonym.
     * @param hard The hard-level synonym.
     * @return A formatted string for the report.
     */
    private String generateReportEntry(String word, String definition, String easy, String medium, String hard) {
        StringBuilder sb = new StringBuilder();
        sb.append("Word: ").append(word).append("\n");
        sb.append("  Definition: ").append(definition).append("\n");
        sb.append("  DefinitionCheck: ").append(checkDefinitionMatchesWord(word, definition)).append("\n");
        sb.append("  Easy: ").append(easy).append(" - Grade: ").append(checkGradeLevel(easy, 1, 5))
          .append("; DefMatch: ").append(checkSynonymMatchesDefinition(easy, definition)).append("\n");
        sb.append("  Medium: ").append(medium).append(" - Grade: ").append(checkGradeLevel(medium, 6, 8))
          .append("; DefMatch: ").append(checkSynonymMatchesDefinition(medium, definition)).append("\n");
        sb.append("  Hard: ").append(hard).append(" - Grade: ").append(checkGradeLevel(hard, 9, 12))
          .append("; DefMatch: ").append(checkSynonymMatchesDefinition(hard, definition)).append("\n");
        return sb.toString();
    }

    /**
     * Writes the report entries to the specified output file.
     * @param report List of report entries.
     * @param outputFilePath Path to the output file.
     */
    private void writeReportToFile(List<String> report, String outputFilePath) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(outputFilePath))) {
            for (String entry : report) {
                writer.write(entry);
                writer.write("\n");
            }
            System.out.println("Report written successfully to: " + outputFilePath);
        } catch (IOException e) {
            System.err.println("Error writing to file: " + e.getMessage());
        }
    }

    /**
     * Uses OpenAI to check if a synonym is appropriate for a given grade range.
     * @param synonym The synonym to check.
     * @param minGrade Minimum grade level.
     * @param maxGrade Maximum grade level.
     * @return OpenAI's response about appropriateness of the word and explanation for its response.
     */
    private String checkGradeLevel(String synonym, int minGrade, int maxGrade) {
        String prompt = String.format(
            "Is the word '%s' appropriate in terms of vocabulary difficulty for students in grades %d to %d, assuming they are participating in an advanced spelling bee or vocabulary competition? " +
            "For reference, %s; %s; %s. " +
            "Ignore social or cultural considerations and focus only on word difficulty. Answer with 'yes' or 'no' and a short explanation.",
            synonym, minGrade, maxGrade, GRADE_REFERENCE_1_5, GRADE_REFERENCE_6_8, GRADE_REFERENCE_9_12
        );
        return callOpenAI(prompt);
    }

    /**
     * Uses OpenAI to check if a synonym matches the given definition.
     * @param synonym The synonym to check.
     * @param definition The definition to compare against.
     * @return OpenAI's response about match of the synonym and defintion and explanation for its response.
     */
    private String checkSynonymMatchesDefinition(String synonym, String definition) {
        String prompt = String.format(
            "Does the word '%s' have the same or very similar meaning as the following definition: '%s'? Answer with 'yes' or 'no' and a short explanation.",
            synonym, definition
        );
        return callOpenAI(prompt);
    }

    /**
     * Uses OpenAI to check if a definition accurately describes the word.
     * @param word The word being checked.
     * @param definition The definition to check.
     * @return OpenAI's response about accuracy of the word's defintion and explanation for its response.
     */
    private String checkDefinitionMatchesWord(String word, String definition) {
        String prompt = String.format(
            "Does the following definition accurately describe the word '%s'? Definition: '%s'. Answer with 'yes' or 'no' and a short explanation.",
            word, definition
        );
        return callOpenAI(prompt);
    }

    /**
     * Helper method to send a prompt to OpenAI and parse the response.
     * @param prompt The prompt to send.
     * @return The content of OpenAI's response, or an error message.
     */
    private String callOpenAI(String prompt) {
        try {
            String response = OpenAIClient.sendTextCompletionRequest(prompt);
            if (response != null && !response.isEmpty()) {
                JsonNode jsonNode = objectMapper.readTree(response);
                String content = jsonNode.path("choices")
                    .path(0)
                    .path("message")
                    .path("content")
                    .asText();
                return content;
            } else {
                return "Error: No response from OpenAI";
            }
        } catch (Exception e) {
            return "Error: " + e.getMessage();
        }
    }

    /**
     * Iteratively improves the definition using OpenAI until it matches the word or maxTries is reached.
     * @param word The word being defined.
     * @param initialDefinition The initial definition.
     * @param maxTries Maximum number of improvement attempts.
     * @return The improved definition.
     */
    private String refineDefinition(String word, String initialDefinition, int maxTries) {
        String definition = initialDefinition;
        for (int i = 0; i < maxTries; i++) {
            // Check if the current definition matches the word.
            String check = checkDefinitionMatchesWord(word, definition);
            if (check.toLowerCase().contains("yes")) {
                return definition;
            }
            
            // Ask OpenAI for a better definition if the current one is not sufficient.
            String prompt = String.format(
                "Suggest a better, more accurate definition for the word '%s'. Only return the definition.",
                word
            );
            String suggestion = callOpenAI(prompt);
            if (suggestion != null && !suggestion.isEmpty() && !suggestion.toLowerCase().contains("error")) {
                definition = suggestion.trim();
            } else {
                break;
            }
        }
        return definition;
    }

    /**
     * Iteratively improves the synonym using OpenAI until it matches the definition and is grade-appropriate, or maxTries is reached.
     * @param word The word for which a synonym is sought.
     * @param definition The definition to match.
     * @param initialSynonym The initial synonym.
     * @param minGrade Minimum grade level.
     * @param maxGrade Maximum grade level.
     * @param maxTries Maximum number of improvement attempts.
     * @return The improved synonym.
     */
    private String refineSynonym(String word, String definition, String initialSynonym, int minGrade, int maxGrade, int maxTries) {
        String synonym = initialSynonym;
        for (int i = 0; i < maxTries; i++) {
            // Check if the synonym matches the definition and is grade-appropriate.
            String matchCheck = checkSynonymMatchesDefinition(synonym, definition);
            String gradeCheck = checkGradeLevel(synonym, minGrade, maxGrade);
            if (matchCheck.toLowerCase().contains("yes") && gradeCheck.toLowerCase().contains("yes")) {
                return synonym;
            }
            
            // Ask OpenAI for a better synonym if the current one is not sufficient.
            String prompt = String.format(
                "Suggest a better synonym for the word '%s' that matches the definition '%s' and is appropriate for students in grades %d-%d. Only return the word.",
                word, definition, minGrade, maxGrade
            );
            String suggestion = callOpenAI(prompt);
            if (suggestion != null && !suggestion.isEmpty() && !suggestion.toLowerCase().contains("error")) {
                synonym = suggestion.trim();
            } else {
                break;
            }
        }
        return synonym;
    }

    /**
     * Writes the improved word list to a file.
     * @param lines List of improved word entries.
     * @param filePath Path to the output file.
     */
    private void writeImprovedWordsFile(List<String> lines, String filePath) {
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(filePath))) {
            for (String line : lines) {
                writer.write(line);
                writer.write("\n");
            }
            System.out.println("Improved words file written to: " + filePath);
        } catch (IOException e) {
            System.err.println("Error writing improved words file: " + e.getMessage());
        }
    }
} 