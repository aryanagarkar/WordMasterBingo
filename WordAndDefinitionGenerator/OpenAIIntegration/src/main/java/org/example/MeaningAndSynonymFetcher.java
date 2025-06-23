package  org.example;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class MeaningAndSynonymFetcher {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static String getDefinitions(String word) {
        System.out.println("Fetching definitions for: " + word); // Debug: show which word is being processed
        String response = OpenAIClient.sendTextCompletionRequest(
            "Give me a simple Definition and 3 synonyms with difficulty level of easy, medium, and hard for the word '" + word + "'," +
            "Format the response as a comma separate list in a single line - " +
            "<put definition here>, <Easy synonym>, <Medium synonym>, <hard synonym>"
        );

        System.out.println("Raw response: " + response); // Debug: print the raw response

        JsonNode responseNode = null;
        try {
            responseNode = objectMapper.readTree(response);
            JsonNode choices = responseNode.get("choices");
            if (choices != null && choices.isArray() && choices.size() > 0) {
                JsonNode firstChoice = choices.get(0);
                if (firstChoice != null) {
                    JsonNode message = firstChoice.get("message");
                    if (message != null) {
                        JsonNode content = message.get("content");
                        if (content != null) {
                            return content.asText();
                        }
                    }
                }
            }
            System.out.println("Warning: Could not find expected fields in response.");
            return "";
        } catch (JsonProcessingException e) {
            System.out.println("JSON parsing error: " + e.getMessage());
            return "";
        }
    }
}
