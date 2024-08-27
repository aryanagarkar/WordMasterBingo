package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;

public class ImageGenerator {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static void main(String[] args) {
        generateImage("Perspective");
    }
    public static void generateImage(String word) {
        String response = OpenAIClient.sendImageGenerationRequest("Generate a playful, uncluttered, and intuitive " +
                "illustration for kids that clearly describes the word 'perspective' using pictures. ");
        System.out.println(response);
      /*  JsonNode responseNode = null;
        try {
            responseNode = objectMapper.readTree(response);
            return responseNode.get("choices").get(0).get("message").get("content").asText();
        } catch (JsonProcessingException e) {
            return "";
        }*/
    }
}
