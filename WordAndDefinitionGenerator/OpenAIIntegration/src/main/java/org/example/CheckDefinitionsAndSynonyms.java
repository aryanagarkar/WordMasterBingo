package org.example;

import java.io.*;
import java.util.*;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class CheckDefinitionsAndSynonyms {
    private static final ObjectMapper objectMapper = new ObjectMapper();
    
    // Constants for better maintainability
    private static final String GRADE_REFERENCE_1_5 = "words like 'forgiveness', 'upset', and 'disaster' are appropriate for grades 1-5";
    private static final String GRADE_REFERENCE_6_8 = "'absolution', 'resilient', and 'debacle' are appropriate for grades 6-8";
    private static final String GRADE_REFERENCE_9_12 = "'obsequious', 'ubiquitous', and 'conundrum' are appropriate for grades 9-12";

    public void runCheck(String inputFilePath, String outputFilePath) {
        // Validate input file exists
        if (!new File(inputFilePath).exists()) {
            System.err.println("Error: Input file not found: " + inputFilePath);
            return;
        }
        
        List<String> report = new ArrayList<>();

        try (BufferedReader reader = new BufferedReader(new FileReader(inputFilePath))) {
            String line;
            int lineNumber = 0;
            while ((line = reader.readLine()) != null) {
                lineNumber++;
                if (line.trim().isEmpty()) continue;
                
                try {
                    String[] parts = line.split(": ", 2);
                    if (parts.length != 2) {
                        System.err.println("Warning: Skipping malformed line " + lineNumber + ": " + line);
                        continue;
                    }
                    
                    String word = parts[0].trim();
                    String[] defAndSyns = parts[1].split(",");
                    if (defAndSyns.length < 4) {
                        System.err.println("Warning: Skipping line " + lineNumber + " - insufficient synonyms: " + line);
                        continue;
                    }
                    
                    String definition = defAndSyns[0].trim();
                    String easy = defAndSyns[1].trim();
                    String medium = defAndSyns[2].trim();
                    String hard = defAndSyns[3].trim();

                    String reportEntry = generateReportEntry(word, definition, easy, medium, hard);
                    report.add(reportEntry);
                    
                } catch (Exception e) {
                    System.err.println("Error processing line " + lineNumber + ": " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Error reading file: " + e.getMessage());
            return;
        }

        // Write the report to the output file
        writeReportToFile(report, outputFilePath);
    }

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

    private String checkGradeLevel(String synonym, int minGrade, int maxGrade) {
        String prompt = String.format(
            "Is the word '%s' appropriate in terms of vocabulary difficulty for students in grades %d to %d, assuming they are participating in an advanced spelling bee or vocabulary competition? " +
            "For reference, %s; %s; %s. " +
            "Ignore social or cultural considerations and focus only on word difficulty. Answer with 'yes' or 'no' and a short explanation.",
            synonym, minGrade, maxGrade, GRADE_REFERENCE_1_5, GRADE_REFERENCE_6_8, GRADE_REFERENCE_9_12
        );
        return callOpenAI(prompt);
    }

    private String checkSynonymMatchesDefinition(String synonym, String definition) {
        String prompt = String.format(
            "Does the word '%s' have the same or very similar meaning as the following definition: '%s'? Answer with 'yes' or 'no' and a short explanation.",
            synonym, definition
        );
        return callOpenAI(prompt);
    }

    private String checkDefinitionMatchesWord(String word, String definition) {
        String prompt = String.format(
            "Does the following definition accurately describe the word '%s'? Definition: '%s'. Answer with 'yes' or 'no' and a short explanation.",
            word, definition
        );
        return callOpenAI(prompt);
    }

    // Helper method to reduce code duplication
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
} 