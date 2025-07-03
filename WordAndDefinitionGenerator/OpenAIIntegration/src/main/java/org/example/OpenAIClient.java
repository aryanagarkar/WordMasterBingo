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

/**
 * Client program for interacting with the OpenAI API for both text and image generation.
 * Handles HTTP requests, authentication, and request/response formatting for the OpenAI.
 */

public class OpenAIClient {
    private static final String API_URL = "https://api.openai.com/";
    private static final String TEXT_COMPLETION_URI = "v1/chat/completions";
    private static final String IMAGE_COMPLETION_URI = "v1/images/generations";
    private static final String API_KEY = System.getenv("API_KEY");
    
    // Configuration constants for timeouts, tokens, and model selection.
    private static final int CONNECT_TIMEOUT_SECONDS = 10;
    private static final int REQUEST_TIMEOUT_MINUTES = 1;
    private static final int MAX_TOKENS = 60;
    private static final String MODEL = "gpt-3.5-turbo";

    private static final HttpClient httpClient = HttpClient.newBuilder()
            .connectTimeout(Duration.ofSeconds(CONNECT_TIMEOUT_SECONDS))
            .build();

    private static final ObjectMapper objectMapper = new ObjectMapper();

    /**
     * Sends an image generation request to the OpenAI API using DALL-E.
     * @param prompt The prompt describing the image to generate.
     * @return The raw JSON response from the API, or an empty string if an error occurs.
     */
    public static String sendImageGenerationRequest(String prompt) {
        try {
            Map<String, Object> requestBody = generateRequestBody(prompt, true);
            return sendPostRequest(API_URL + IMAGE_COMPLETION_URI, requestBody);
        } catch (Exception ex) {
            return "";
        }
    }

    /**
     * Sends a text completion request to the OpenAI API.
     * @param prompt The prompt to send to the model.
     * @return The raw JSON response from the API, or an empty string if an error occurs.
     */
    public static String sendTextCompletionRequest(String prompt) {
        try {
            return sendPostRequest(API_URL + TEXT_COMPLETION_URI, generateRequestBody(prompt, false));
        } catch (Exception ex) {
            System.err.println("Error in text completion request: " + ex.getMessage());
            return "";
        }
    }

    /**
     * Generates the request body for either text or image generation requests.
     * For image requests, the map contains keys: "prompt", "model", "size", and "n".
     * For text requests, the map contains keys: "messages" (a list of system/user message maps), "max_tokens", and "model".
     *
     * @param prompt The prompt for the request.
     * @param isImageRequest True if the request is for image generation, false for text.
     * @return The request body as a map suitable for serialization to JSON for the OpenAI API.
     */
    private static Map<String, Object> generateRequestBody(String prompt, boolean isImageRequest) {
        try {
            if (isImageRequest) {
                // Build request body for image generation.
                Map<String, Object> requestBody = new HashMap<>();
                requestBody.put("prompt", prompt);
                requestBody.put("model", "dall-e-3");
                requestBody.put("size", "1024x1024");
                requestBody.put("n", 1);
                return requestBody;
            } else {
                // Build request body for text completion (chat).
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

    /**
     * Sends a POST request to the specified OpenAI endpoint with the given request body.
     * Handles authentication and error checking.
     * @param url The full URL to send the request to.
     * @param requestBody The request body as a map.
     * @return The response body as a string if successful.
     * @throws Exception if the API key is missing, the request body is null, or the request fails.
     */
    
    private static String sendPostRequest(String url, Map<String, Object> requestBody) throws Exception {
        // Check for required API key.
        if (API_KEY == null || API_KEY.trim().isEmpty()) {
            throw new RuntimeException("API_KEY environment variable is not set");
        }
        
        // Check for valid request body.
        if (requestBody == null) {
            throw new RuntimeException("Request body is null");
        }
        
        // Convert the request body map to JSON.
        String requestBodyJson = objectMapper.writeValueAsString(requestBody);

        // Build the HTTP request.
        HttpRequest request = HttpRequest.newBuilder()
                .uri(new URI(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + API_KEY)
                .timeout(Duration.ofMinutes(REQUEST_TIMEOUT_MINUTES))
                .POST(HttpRequest.BodyPublishers.ofString(requestBodyJson))
                .build();

        // Send the request and get the response.
        HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
        
        // Check for successful response.
        if (response.statusCode() == 200) {
            return response.body();
        } else {
            throw new RuntimeException("API request failed with status code: " + response.statusCode() + 
                                     ", Response: " + response.body());
        }
    }
}
