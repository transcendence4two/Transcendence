package com.ecole42.exception;

public class UserAlreadyExistsException extends RuntimeException {
    
    public static final String USER_ALREADY_EXISTS = "User or email already registered";
    
    public UserAlreadyExistsException() {
        super(USER_ALREADY_EXISTS);
    }
    
    public UserAlreadyExistsException(String message) {
        super(message);
    }
    
    public UserAlreadyExistsException(String message, Throwable cause) {
        super(message, cause);
    }
}
