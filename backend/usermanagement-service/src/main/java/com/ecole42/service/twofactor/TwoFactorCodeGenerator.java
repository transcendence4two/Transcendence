package com.ecole42.service.twofactor;

import jakarta.enterprise.context.ApplicationScoped;
import java.security.SecureRandom;

@ApplicationScoped
public class TwoFactorCodeGenerator {
    private static final int CODE_UPPER_BOUND = 900000;
    private static final int CODE_LOWER_BOUND = 100000;
    
    private final SecureRandom secureRandom = new SecureRandom();

    public String generate() {
        int value = secureRandom.nextInt(CODE_UPPER_BOUND) + CODE_LOWER_BOUND;
        return String.valueOf(value);
    }
}
