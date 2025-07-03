package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Utility class for generating simple educational images for vocabulary words using the OpenAI API.
 *
 * Note: This class is not currently used in the application because the generated images are still too complex
 * and do not meet the requirements for minimal, child-friendly illustrations.
 */
public class ImageGenerator {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Attempts to generate an educational image for the given word using OpenAI's image API.
     * Currently not used, as the generated images are too complex.
     * @param word The vocabulary word to illustrate.
     */
    public static void generateImage(String word) {        
        String prompt = createSimplePrompt(word);
        String response = OpenAIClient.sendImageGenerationRequest(prompt);
        System.out.println(response);
    }
    
    /**
     * Creates a prompt for OpenAI to generate a minimal, child-friendly illustration for a word.
     * @param word The vocabulary word to illustrate.
     * @return The prompt string for the image generation API.
     */
    private static String createSimplePrompt(String word) {
        return "Create a simple educational diagram: " +
               "White background. " +
               "Draw exactly 2-3 simple objects. " +
               "Use only basic shapes (circles, squares, triangles). " +
               "Use only 3-4 bright colors (red, blue, yellow, green). " +
               "Show the meaning of '" + word + "' clearly. " +
               "No text, no complex details, no abstract patterns. " +
               "Style: minimal, clean, like a children's textbook illustration.";
    }
}
