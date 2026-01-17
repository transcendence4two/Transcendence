package com.ecole42.mapper;

import com.ecole42.domain.entity.User;
import com.ecole42.dto.request.UserRegistrationRequest;
import com.ecole42.dto.response.UserRegistrationResponse;
import com.ecole42.security.PasswordEncoder;
import jakarta.enterprise.context.ApplicationScoped;

@ApplicationScoped
public class UserMapper {
    
    private final PasswordEncoder passwordEncoder;
    
    public UserMapper(PasswordEncoder passwordEncoder) {
        this.passwordEncoder = passwordEncoder;
    }
    
    public User toDomain(UserRegistrationRequest request) {
        User user = new User();
        user.username = request.username();
        user.email = request.email();
        user.password = passwordEncoder.encode(request.password());
        user.twoFactorEnabled = request.enable2fa() != null && request.enable2fa();
        return (user);
    }
    
    public UserRegistrationResponse toResponse(User user) {
        return (new UserRegistrationResponse(
            user.id,
            "User registered successfully",
            user.createdAt)
        );
    }
}
