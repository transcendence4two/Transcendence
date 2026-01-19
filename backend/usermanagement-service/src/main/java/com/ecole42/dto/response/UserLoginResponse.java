package com.ecole42.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;

public record UserLoginResponse (
    @JsonProperty("two_factor_required")
    boolean twoFactorRequired,

    @JsonProperty("access_token")
    String accessToken,

    @JsonProperty("user_id")
    Long userId,

    @JsonProperty("username")
    String username,

    @JsonProperty("email")
    String email
) {}
