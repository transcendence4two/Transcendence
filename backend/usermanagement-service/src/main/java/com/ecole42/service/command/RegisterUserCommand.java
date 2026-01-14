package com.ecole42.service.command;

import com.ecole42.domain.entity.User;
import com.ecole42.domain.repository.UserRepository;
import com.ecole42.dto.request.UserRegistrationRequest;
import com.ecole42.dto.response.UserRegistrationResponse;
import com.ecole42.exception.UserAlreadyExistsException;
import com.ecole42.mapper.UserMapper;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.transaction.Transactional;

@ApplicationScoped
public class RegisterUserCommand implements UserCommand<UserRegistrationRequest, UserRegistrationResponse> {
    
    private final UserRepository userRepository;
    private final UserMapper userMapper;
    
    public RegisterUserCommand(UserRepository userRepository, UserMapper userMapper) {
        this.userRepository = userRepository;
        this.userMapper = userMapper;
    }
    
    @Override
    @Transactional
    public UserRegistrationResponse execute(UserRegistrationRequest input) {
        validateUniqueEmailAndUsername(input.email(), input.username());
        
        User user = userMapper.toDomain(input);
        userRepository.persist(user);
        return (userMapper.toResponse(user));
    }
    
    private void validateUniqueEmailAndUsername(String email, String username) {
        if (userRepository.findByEmail(email).isPresent()) {
            throw new UserAlreadyExistsException("Email already registered");
        }
        
        if (userRepository.findByUsername(username).isPresent()) {
            throw new UserAlreadyExistsException("Username already registered");
        }
    }
}
