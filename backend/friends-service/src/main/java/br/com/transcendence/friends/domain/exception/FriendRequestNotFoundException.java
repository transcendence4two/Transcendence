package br.com.transcendence.friends.domain.exception;

import java.util.UUID;

public class FriendRequestNotFoundException extends DomainException {
    public FriendRequestNotFoundException(UUID id) {
        super("Friend request with id " + id + " not found");
    }

    @Override
    public int httpStatus() {
        return 404;
    }
}
