package br.com.transcendence.friends.domain.exception;

public class FriendshipNotFoundException extends DomainException {
    public FriendshipNotFoundException(String userId1, String userId2) {
        super("Active friendship not found between users " + userId1 + " and " + userId2);
    }

    @Override
    public int httpStatus() {
        return 404;
    }
}
