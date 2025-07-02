package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;

public class ImageGenerator {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static void generateImage(String word) {        
        String prompt = createSimplePrompt(word);
        String response = OpenAIClient.sendImageGenerationRequest(prompt);
        System.out.println(response);
    }
    
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
    
      /*  JsonNode responseNode = null;
        try {
            responseNode = objectMapper.readTree(response);
            return responseNode.get("choices").get(0).get("message").get("content").asText();
        } catch (JsonProcessingException e) {
            return "";
        }*/
}
