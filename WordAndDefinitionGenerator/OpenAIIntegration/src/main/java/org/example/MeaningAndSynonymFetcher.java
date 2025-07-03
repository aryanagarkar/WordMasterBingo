package  org.example;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * Utility class for fetching a simple definition and three synonyms (easy, medium, hard) for a given word
 * using the OpenAI API. The response is returned in a comma-separated single line format.
 */

public class MeaningAndSynonymFetcher {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Fetches a simple definition and three synonyms (easy, medium, hard) for the given word from OpenAI.
     * The response is returned in the format: <definition>, <easy synonym>, <medium synonym>, <hard synonym>
     *
     * @param word The word to fetch the definition and synonyms for.
     * @return The definition and synonyms as a comma-separated string, or an empty string if parsing fails.
     */
    public static String getDefinitions(String word) {
        // Send a prompt to OpenAI to get a definition and three synonyms.
        String response = OpenAIClient.sendTextCompletionRequest(
            "Give me a simple Definition and 3 synonyms with difficulty level of easy, medium, and hard for the word '" + word + "'," +
            "Format the response as a comma separate list in a single line - " +
            "<put definition here>, <Easy synonym>, <Medium synonym>, <hard synonym>"
        );

        System.out.println("Raw response: " + response); // Debug: print the raw response

        JsonNode responseNode = null;
        try {
            // Parse the JSON response from OpenAI.
            responseNode = objectMapper.readTree(response);
            JsonNode choices = responseNode.get("choices");
            if (choices != null && choices.isArray() && choices.size() > 0) {
                JsonNode firstChoice = choices.get(0);
                if (firstChoice != null) {
                    JsonNode message = firstChoice.get("message");
                    if (message != null) {
                        JsonNode content = message.get("content");
                        if (content != null) {
                            // Return the content string (definition and synonyms).
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
