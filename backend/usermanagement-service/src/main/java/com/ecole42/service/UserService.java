package com.ecole42.service;

import com.ecole42.dto.request.UserLoginRequest;
import com.ecole42.dto.request.UserRegistrationRequest;
import com.ecole42.dto.response.UserLoginResponse;
import com.ecole42.dto.response.UserRegistrationResponse;
import com.ecole42.service.command.LoginUserCommand;
import com.ecole42.service.command.RegisterUserCommand;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class UserService {
    
    private final RegisterUserCommand registerUserCommand;
    private final LoginUserCommand loginUserCommand;
    
    public UserService(
        RegisterUserCommand registerUserCommand,
        LoginUserCommand loginUserCommand
    ) {
        this.registerUserCommand = registerUserCommand;
        this.loginUserCommand = loginUserCommand;
    }
    
    public UserRegistrationResponse register(UserRegistrationRequest request) {
        return registerUserCommand.execute(request);
    }
    
    public UserLoginResponse login(UserLoginRequest request) {
        return loginUserCommand.execute(request);
    }
}
