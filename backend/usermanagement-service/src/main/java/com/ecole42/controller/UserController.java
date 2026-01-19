package com.ecole42.controller;

import com.ecole42.dto.request.UserLoginRequest;
import com.ecole42.dto.request.UserRegistrationRequest;
import com.ecole42.dto.response.UserLoginResponse;
import com.ecole42.dto.response.UserRegistrationResponse;
import com.ecole42.service.UserService;

import jakarta.validation.Valid;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.openapi.annotations.tags.Tag;


@Path("/users")
@Consumes(MediaType.APPLICATION_JSON)
@Produces(MediaType.APPLICATION_JSON)
@Tag(name = "User Management", description = "APIs para gerenciamento de usuários")
public class UserController {
    
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @POST
    @Path("/register")
    public Response register(@Valid UserRegistrationRequest registrationRequest) {
        UserRegistrationResponse response = userService.register(registrationRequest);
        return (Response
            .status(Response.Status.CREATED)
            .type(MediaType.APPLICATION_JSON)
            .entity(response)
            .build());
    }

    @POST
    @Path("/login")
    public Response login(@Valid UserLoginRequest loginRequest) {
        UserLoginResponse response = userService.login(loginRequest);
        Response.Status status = response.twoFactorRequired()
            ? Response.Status.ACCEPTED
            : Response.Status.OK;

        return (Response
            .status(status)
            .type(MediaType.APPLICATION_JSON)
            .entity(response)
            .build());
    }
}
