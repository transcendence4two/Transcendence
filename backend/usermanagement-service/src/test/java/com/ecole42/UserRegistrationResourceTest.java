package com.ecole42;

import io.quarkus.test.junit.QuarkusTest;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.CoreMatchers.notNullValue;

@QuarkusTest
class UserRegistrationResourceTest {

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
            .statusCode(201)
            .body("id", notNullValue())
            .body("message", is("User registered successfully"));
    }
}
