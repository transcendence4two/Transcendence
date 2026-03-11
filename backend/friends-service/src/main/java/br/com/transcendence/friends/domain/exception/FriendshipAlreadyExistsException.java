package br.com.transcendence.friends.domain.exception;

public class FriendshipAlreadyExistsException extends DomainException {
    public FriendshipAlreadyExistsException(String message) {
        super(message);
    }

    @Override
    public int httpStatus() {
        return 409;
    }
}
