package com.ecole42.service;

import com.ecole42.dto.request.UserRegistrationRequest;
import com.ecole42.dto.response.UserRegistrationResponse;
import com.ecole42.service.command.RegisterUserCommand;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class UserService {
    
    private final RegisterUserCommand registerUserCommand;
    
    public UserService(RegisterUserCommand registerUserCommand) {
        this.registerUserCommand = registerUserCommand;
    }
    
    public UserRegistrationResponse register(UserRegistrationRequest request) {
        return registerUserCommand.execute(request);
    }
}
