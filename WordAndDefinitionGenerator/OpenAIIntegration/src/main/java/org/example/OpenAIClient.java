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
    
    // Configuration constants
    private static final int CONNECT_TIMEOUT_SECONDS = 10;
    private static final int REQUEST_TIMEOUT_MINUTES = 1;
    private static final int MAX_TOKENS = 60;
    private static final String MODEL = "gpt-3.5-turbo";

    private static final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(CONNECT_TIMEOUT_SECONDS))
            .build();

    private static final ObjectMapper objectMapper = new ObjectMapper();

    public static String sendImageGenerationRequest(String prompt) {
        try {
            return sendPostRequest(API_URL + IMAGE_COMPLETION_URI, generateRequestBody(prompt, true));
        } catch (Exception ex) {
            System.err.println("Error in image generation request: " + ex.getMessage());
            return "";
        }
    }

    public static String sendTextCompletionRequest(String prompt) {
        try {
            return sendPostRequest(API_URL + TEXT_COMPLETION_URI, generateRequestBody(prompt, false));
        } catch (Exception ex) {
            System.err.println("Error in text completion request: " + ex.getMessage());
            return "";
        }
    }

    private static Map<String, Object> generateRequestBody(String prompt, boolean isImageRequest) {
        try {
            if (isImageRequest) {
                Map<String, Object> requestBody = new HashMap<>();
                requestBody.put("prompt", prompt);
                return requestBody;
            } else {
                List<Map<String, String>> messages = new ArrayList<>();
                
                Map<String, String> systemMessage = new HashMap<>();
                systemMessage.put("role", "system");
                systemMessage.put("content", "You are a helpful assistant.");
                messages.add(systemMessage);

                Map<String, String> userMessage = new HashMap<>();
                userMessage.put("role", "user");
                userMessage.put("content", prompt);
                messages.add(userMessage);

                Map<String, Object> requestBody = new HashMap<>();
                requestBody.put("messages", messages);
                requestBody.put("max_tokens", MAX_TOKENS);
                requestBody.put("model", MODEL);
                return requestBody;
            }
        } catch (Exception e) {
            System.err.println("Error generating request body: " + e.getMessage());
            return null;
        }
    }

    private static String sendPostRequest(String url, Map<String, Object> requestBody) throws Exception {
        if (API_KEY == null || API_KEY.trim().isEmpty()) {
            throw new RuntimeException("API_KEY environment variable is not set");
        }
        
        if (requestBody == null) {
            throw new RuntimeException("Request body is null");
        }
        
        String requestBodyJson = objectMapper.writeValueAsString(requestBody);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .timeout(Duration.ofMinutes(REQUEST_TIMEOUT_MINUTES))
                .POST(HttpRequest.BodyPublishers.ofString(requestBodyJson))
                .build();

        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        if (response.statusCode() == 200) {
            return response.body();
        } else {
            throw new RuntimeException("API request failed with status code: " + response.statusCode() + 
                                     ", Response: " + response.body());
        }
    }
}
