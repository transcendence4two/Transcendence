package com.ecole42.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.time.LocalDateTime;

public record UserRegistrationResponse(
    @JsonProperty("id")
    Long id,
    
    @JsonProperty("message")
    String message,
    
    @JsonProperty("created_at")
    LocalDateTime createdAt
) {}
