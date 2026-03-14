package br.com.transcendence.friends.infrastructure.rest;

import br.com.transcendence.friends.application.dto.SendRequestDTO;
import br.com.transcendence.friends.application.port.out.UserManagementPort;
import io.quarkus.test.InjectMock;
import io.quarkus.test.junit.QuarkusTest;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.Test;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.notNullValue;

@QuarkusTest
class RequestsResourceTest {

    @InjectMock
    UserManagementPort userManagementPort;

    @Test
    void testSendRequestEndpoint() {
        when(userManagementPort.userExists(anyString())).thenReturn(true);
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
