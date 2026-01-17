package com.ecole42;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;
import jakarta.inject.Inject;
import io.quarkus.test.junit.QuarkusMock;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.anyOf;

import com.ecole42.domain.repository.UserRepository;
import com.ecole42.domain.entity.User;
import com.ecole42.security.PasswordEncoder;
import com.ecole42.service.command.RegisterUserCommand;

@QuarkusTest
class UserRegistrationResourceTest {

    @Inject
    UserRepository userRepository;

    @Inject
    PasswordEncoder passwordEncoder;

    @Test
    void testSuccessfulRegistration() {
        String payload = """
            {
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecurePass123!",
                "enable_2fa": true
            }
            """;

        given()
            .contentType("application/json")
            .body(payload)
        .when()
            .post("/users/register")
        .then()
            .statusCode(201);

        User user = userRepository.findByEmail("test@example.com").orElseThrow();
        org.junit.jupiter.api.Assertions.assertNotNull(user.id);
        org.junit.jupiter.api.Assertions.assertTrue(Boolean.TRUE.equals(user.twoFactorEnabled));
        org.junit.jupiter.api.Assertions.assertTrue(
            passwordEncoder.matches("SecurePass123!", user.password),
            "Password should be stored as BCrypt hash"
        );
    }

    @Test
    void testDuplicateEmail() {
        String first = """
            {
                "username": "user1",
                "email": "dup@example.com",
                "password": "Pass12345!",
                "enable_2fa": false
            }
            """;

        given()
            .contentType("application/json")
            .body(first)
        .when()
            .post("/users/register")
        .then()
            .statusCode(201);

        String second = """
            {
                "username": "user2",
                "email": "dup@example.com",
                "password": "Pass12345!",
                "enable_2fa": true
            }
            """;

        given()
            .contentType("application/json")
            .body(second)
        .when()
            .post("/users/register")
        .then()
            .statusCode(anyOf(is(409)));

        long countByEmail = com.ecole42.domain.entity.User.count("email", "dup@example.com");
        org.junit.jupiter.api.Assertions.assertEquals(1L, countByEmail, "Duplicate email should not create a second user");
    }

    @Test
    void testDuplicateUsername() {
        String first = """
            {
                "username": "sameuser",
                "email": "email1@example.com",
                "password": "Pass12345!",
                "enable_2fa": false
            }
            """;

        given()
            .contentType("application/json")
            .body(first)
        .when()
            .post("/users/register")
        .then()
            .statusCode(201);

        String second = """
            {
                "username": "sameuser",
                "email": "email2@example.com",
                "password": "Pass12345!",
                "enable_2fa": false
            }
            """;

        given()
            .contentType("application/json")
            .body(second)
        .when()
            .post("/users/register")
        .then()
            .statusCode(anyOf(is(409)));

        long countByUsername = com.ecole42.domain.entity.User.count("username", "sameuser");
        org.junit.jupiter.api.Assertions.assertEquals(1L, countByUsername, "Duplicate username should not create a second user");
    }

    @Test
    void testPasswordHashAndTwoFactorPersisted() {
        String rawPassword = "SecretPass987!";
        String email = "persist@example.com";

        String payload = String.format("""
            {
                "username": "persistuser",
                "email": "%s",
                "password": "%s",
                "enable_2fa": true
            }
            """, email, rawPassword);

        given()
            .contentType("application/json")
            .body(payload)
        .when()
            .post("/users/register")
        .then()
            .statusCode(201);

        User user = userRepository.findByEmail(email).orElseThrow();
        org.junit.jupiter.api.Assertions.assertTrue(
            passwordEncoder.matches(rawPassword, user.password),
            "Password should be stored as a BCrypt hash matching the raw password"
        );
        org.junit.jupiter.api.Assertions.assertTrue(
            Boolean.TRUE.equals(user.twoFactorEnabled),
            "Two-factor preference should be persisted as true"
        );
    }

    @Test
    void testInternalServerError() {
        RegisterUserCommand failing = new RegisterUserCommand(userRepository, new com.ecole42.mapper.UserMapper(passwordEncoder)) {
            @Override
            public com.ecole42.dto.response.UserRegistrationResponse execute(com.ecole42.dto.request.UserRegistrationRequest input) {
                throw new RuntimeException("Unexpected failure");
            }
        };
        QuarkusMock.installMockForType(failing, RegisterUserCommand.class);

        String payload = """
            {
                "username": "erruser",
                "email": "err@example.com",
                "password": "Pass12345!",
                "enable_2fa": false
            }
            """;

        given()
            .contentType("application/json")
            .body(payload)
        .when()
            .post("/users/register")
        .then()
            .statusCode(500)
            .body("error", is("Internal server error"));
    }
}
