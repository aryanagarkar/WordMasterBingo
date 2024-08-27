package  org.example;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;

public class MeaningAndSynonymFetcher {

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static String getDefinitions(String word) {
        String response = OpenAIClient.sendTextCompletionRequest("Give me a simple Definition and 3 synonyms with difficulty level of easy, medium, and hard for the word '" + word + "'." +
                "Format the response as a coma separate list in a single line - " +
                "Definition:<put definition here>, Easy:<Easy synonym>, Medium: <Medium synonym>, Hard: <hard synonym>");

        JsonNode responseNode = null;
        try {
            responseNode = objectMapper.readTree(response);
            return responseNode.get("choices").get(0).get("message").get("content").asText();
        } catch (JsonProcessingException e) {
            return "";
        }
    }
}
