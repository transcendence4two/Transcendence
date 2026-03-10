package br.com.transcendence.friends.domain.exception;

public class UserNotFoundException extends DomainException {
    public UserNotFoundException(String userId) {
        super("User with id " + userId + " not found");
    }
}
