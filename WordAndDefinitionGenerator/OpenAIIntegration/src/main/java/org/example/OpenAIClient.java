package org.example;

import com.fasterxml.jackson.databind.ObjectMapper;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class OpenAIClient {
    private static final String API_URL = "https://api.openai.com/";
    private static final String TEXT_COMPLETION_URI = "v1/chat/completions";
    private static final String IMAGE_COMPLETION_URI = "v1/images/generations";
    private static final String API_KEY = System.getenv("API_KEY");

    private static final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(10))
            .build();

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static String sendImageGenerationRequest(String prompt) {
        try {
            return sendPostRequest(API_URL + IMAGE_COMPLETION_URI, generateRequestBody(prompt, true));
        } catch (Exception ex) {
            return "";
        }
    }

    public static String sendTextCompletionRequest(String prompt) {
        try {
            return sendPostRequest(API_URL + TEXT_COMPLETION_URI, generateRequestBody(prompt, false));
        } catch (Exception ex) {
            return "";
        }
    }

    private static Map<String, Object> generateRequestBody(String prompt, boolean isImageRequest) {
        try {
            List<Map<String, String>> messages = new ArrayList<>();
            Map<String, String> systemMessage = new HashMap<>();
            systemMessage.put("role", "system");
            systemMessage.put("content", "You are a helpful assistant.");
            messages.add(systemMessage);

            Map<String, String> userMessage = new HashMap<>();
            userMessage.put("role", "user");
            userMessage.put("content", prompt);
            messages.add(userMessage);

            // Example request parameters
            Map<String, Object> requestBody = new HashMap<>();
            if (isImageRequest) {
                requestBody.put("prompt", prompt);
            } else {
                requestBody.put("messages", messages);
                requestBody.put("max_tokens", 60);
                requestBody.put("model", "gpt-3.5-turbo");
            }
            return requestBody;
        } catch (Exception e) {
            return null;
        }
    }

    private static String sendPostRequest(String url, Map<String, Object> requestBody) throws Exception {
        String requestBodyJson = objectMapper.writeValueAsString(requestBody);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .timeout(Duration.ofMinutes(1))
                .POST(HttpRequest.BodyPublishers.ofString(requestBodyJson))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        if (response.statusCode() == 200) {
            //JsonNode responseNode = objectMapper.readTree(response.body());
            //System.out.println(response.body());
            return response.body();
            //return response.body();
        } else {
            throw new RuntimeException("Failed: HTTP error code : " + response.statusCode());
        }
    }
}
