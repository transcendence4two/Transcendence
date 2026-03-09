package br.com.transcendence.friends.domain.exception;

public class FriendRequestAlreadyExistsException extends DomainException {
    public FriendRequestAlreadyExistsException(String message) {
        super(message);
    }
}
