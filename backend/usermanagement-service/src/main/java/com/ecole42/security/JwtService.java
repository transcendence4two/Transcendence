package com.ecole42.security;

import com.ecole42.domain.entity.User;
import io.smallrye.jwt.build.Jwt;
import jakarta.enterprise.context.ApplicationScoped;
import org.eclipse.microprofile.config.inject.ConfigProperty;

@ApplicationScoped
public class JwtService {
    @ConfigProperty(name = "jwt.secret")
    String jwtSecret;

    @ConfigProperty(name = "jwt.issuer")
    String issuer;

    @ConfigProperty(name = "jwt.expiration.seconds")
    long expirationSeconds;

    public String generateAccessToken(User user) {
        return Jwt
            .issuer(issuer)
            .subject(String.valueOf(user.id))
            .expiresIn(expirationSeconds)
            .claim("email", user.email)
            .claim("username", user.username)
            .claim("two_factor_enabled", user.twoFactorEnabled)
            .signWithSecret(jwtSecret);
    }
}
