package com.ecole42.service.command;

import com.ecole42.domain.entity.User;
import com.ecole42.domain.repository.UserRepository;
import com.ecole42.dto.request.UserLoginRequest;
import com.ecole42.dto.response.UserLoginResponse;
import com.ecole42.exception.InvalidCredentialsException;
import com.ecole42.security.JwtService;
import com.ecole42.security.PasswordEncoder;
import com.ecole42.service.twofactor.TwoFactorCodeGenerator;
import com.ecole42.service.twofactor.TwoFactorNotifier;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class LoginUserCommand implements UserCommand<UserLoginRequest, UserLoginResponse> {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;
    private final TwoFactorNotifier twoFactorNotifier;
    private final TwoFactorCodeGenerator codeGenerator;

    @Inject
    public LoginUserCommand(
        UserRepository userRepository,
        PasswordEncoder passwordEncoder,
        JwtService jwtService,
        TwoFactorNotifier twoFactorNotifier,
        TwoFactorCodeGenerator codeGenerator
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
        this.twoFactorNotifier = twoFactorNotifier;
        this.codeGenerator = codeGenerator;
    }

    @Override
    public UserLoginResponse execute(UserLoginRequest input) {
        User user = authenticateUser(input);

        if (requiresTwoFactor(user)) {
            return handleTwoFactorFlow(user);
        }

        return handleStandardLogin(user);
    }

    private User authenticateUser(UserLoginRequest input) {
        User user = userRepository.findByEmail(input.email())
            .orElseThrow(() -> new InvalidCredentialsException("Invalid email or password"));

        if (!passwordEncoder.matches(input.password(), user.password))
            throw new InvalidCredentialsException("Invalid email or password");

        return (user);
    }

    private boolean requiresTwoFactor(User user) {
        return Boolean.TRUE.equals(user.twoFactorEnabled);
    }

    private UserLoginResponse handleTwoFactorFlow(User user) {
        String code = codeGenerator.generate();
        twoFactorNotifier.sendCode(user, code);
        
        return (new UserLoginResponse(
            true,
            null,
            user.id,
            user.username,
            user.email
        ));
    }

    private UserLoginResponse handleStandardLogin(User user) {
        String token = jwtService.generateAccessToken(user);
        
        return (new UserLoginResponse(
            false,
            token,
            user.id,
            user.username,
            user.email
        ));
    }
}
