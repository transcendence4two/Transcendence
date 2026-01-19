package com.ecole42;

import com.ecole42.domain.entity.User;
import com.ecole42.domain.repository.UserRepository;
import com.ecole42.dto.request.UserLoginRequest;
import com.ecole42.dto.response.UserLoginResponse;
import com.ecole42.security.JwtService;
import com.ecole42.security.PasswordEncoder;
import com.ecole42.service.command.LoginUserCommand;
import com.ecole42.service.twofactor.MockTwoFactorNotifier;
import com.ecole42.service.twofactor.TwoFactorCodeGenerator;
import io.quarkus.test.junit.QuarkusMock;
import io.quarkus.test.junit.QuarkusTest;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.Mockito;

import static io.restassured.RestAssured.given;
import static org.hamcrest.CoreMatchers.is;
import static org.hamcrest.Matchers.emptyOrNullString;
import static org.hamcrest.Matchers.not;
import static org.mockito.ArgumentMatchers.any;

@QuarkusTest
class UserLoginResourceTest {

    @Inject
    UserRepository userRepository;

    @Inject
    PasswordEncoder passwordEncoder;

    @Inject
    JwtService jwtService;

    @Inject
    MockTwoFactorNotifier mockTwoFactorNotifier;

    @Inject
    TwoFactorCodeGenerator codeGenerator;

    @BeforeEach
    @Transactional
    void cleanDatabase() {
        userRepository.deleteAll();
        JwtService jwtMock = Mockito.mock(JwtService.class);
        Mockito.when(jwtMock.generateAccessToken(any(User.class))).thenReturn("dummy-token");
        QuarkusMock.installMockForType(jwtMock, JwtService.class);
    }

    @Test
    void loginSuccessWithoutTwoFactor() {
        createUser("loginuser1", "login1@example.com", "PlainPass123", false);

        given()
            .contentType("application/json")
            .body(new UserLoginRequest("login1@example.com", "PlainPass123"))
        .when()
            .post("/users/login")
        .then()
            .statusCode(200)
            .body("two_factor_required", is(false))
            .body("access_token", not(emptyOrNullString()))
            .body("username", is("loginuser1"))
            .body("email", is("login1@example.com"));
    }

    @Test
    void loginSuccessWithTwoFactor() {
        createUser("loginuser2", "login2@example.com", "PlainPass123", true);

        given()
            .contentType("application/json")
            .body(new UserLoginRequest("login2@example.com", "PlainPass123"))
        .when()
            .post("/users/login")
        .then()
            .statusCode(202)
            .body("two_factor_required", is(true))
            .body("access_token", emptyOrNullString())
            .body("username", is("loginuser2"))
            .body("email", is("login2@example.com"));
    }

    @Test
    void loginWithInvalidCredentialsReturnsUnauthorized() {
        createUser("loginuser3", "login3@example.com", "PlainPass123", false);

        String payload = """
            {
                \"email\": \"login3@example.com\",
                \"password\": \"WrongPass999\"
            }
            """;

        given()
            .contentType("application/json")
            .body(payload)
        .when()
            .post("/users/login")
        .then()
            .statusCode(401)
            .body("error", is("Invalid email or password"));
    }

    @Test
    void internalErrorReturnsServerError() {
        LoginUserCommand failing = new LoginUserCommand(
            userRepository,
            passwordEncoder,
            jwtService,
            mockTwoFactorNotifier,
            codeGenerator
        ) {
            @Override
            public UserLoginResponse execute(UserLoginRequest input) {
                throw new RuntimeException("Unexpected failure");
            }
        };
        QuarkusMock.installMockForType(failing, LoginUserCommand.class);

        String payload = """
            {
                \"email\": \"any@example.com\",
                \"password\": \"AnyPassword1!\"
            }
            """;

        given()
            .contentType("application/json")
            .body(payload)
        .when()
            .post("/users/login")
        .then()
            .statusCode(500)
            .body("error", is("Internal server error"));
    }

    @Transactional
    void createUser(String username, String email, String rawPassword, boolean twoFactor) {
        User user = new User();
        user.username = username;
        user.email = email;
        user.password = passwordEncoder.encode(rawPassword);
        user.twoFactorEnabled = twoFactor;
        userRepository.persist(user);
    }
}
