package com.ecole42.dto.request;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;

public record UserLoginRequest ( 
    
    @NotBlank(message = "Email is required")
    @Email(message = "Email must be valid")
    @JsonProperty("email")
    String email,

    @NotBlank(message = "Password is required")
    @JsonProperty("password")
    String password
) {}
