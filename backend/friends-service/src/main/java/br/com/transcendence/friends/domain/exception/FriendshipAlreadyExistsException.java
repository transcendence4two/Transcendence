package br.com.transcendence.friends.domain.exception;

public class FriendshipAlreadyExistsException extends DomainException {
    public FriendshipAlreadyExistsException(String message) {
        super(message);
    }
}
