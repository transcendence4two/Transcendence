package br.com.transcendence.friends.infrastructure.rest.util;

import jakarta.ws.rs.NotAuthorizedException;

public final class UserContextHelper {

    private UserContextHelper() {}

    public static String extractUserId(String headerUserId) {
        if (headerUserId == null || headerUserId.isBlank()) {
            throw new NotAuthorizedException("X-User-Id header is required for context");
        }
        return headerUserId;
    }
}
