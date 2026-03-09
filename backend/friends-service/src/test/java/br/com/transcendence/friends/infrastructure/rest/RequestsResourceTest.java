package br.com.transcendence.friends.infrastructure.rest;

import br.com.transcendence.friends.application.dto.SendRequestDTO;
import io.quarkus.test.junit.QuarkusTest;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.notNullValue;

@QuarkusTest
class RequestsResourceTest {

    @Test
    void testSendRequestEndpoint() {
        SendRequestDTO dto = new SendRequestDTO("userB");

        given()
          .contentType(ContentType.JSON)
          .header("X-User-Id", "userA")
          .body(dto)
        .when()
          .post("/friends/requests")
        .then()
          .statusCode(201)
          .body("id", notNullValue());
    }

    @Test
    void testListPendingRequestsEndpoint() {
        given()
          .header("X-User-Id", "userA")
        .when()
          .get("/friends/requests")
        .then()
          .statusCode(200);
    }
}
