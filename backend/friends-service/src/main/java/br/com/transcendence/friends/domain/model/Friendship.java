package br.com.transcendence.friends.domain.model;

import java.time.LocalDateTime;
import java.util.UUID;

public record Friendship(
    UUID id,
    String userId1,
    String userId2,
    boolean active,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {
    public static Friendship create(String userId1, String userId2) {
        if (userId1.equals(userId2)) {
            throw new IllegalArgumentException("Cannot create friendship with yourself");
        }
        String u1 = userId1.compareTo(userId2) < 0 ? userId1 : userId2;
        String u2 = userId1.compareTo(userId2) < 0 ? userId2 : userId1;

        return new Friendship(
            UUID.randomUUID(),
            u1,
            u2,
            true,
            LocalDateTime.now(),
            LocalDateTime.now()
        );
    }

    public Friendship deactivate() {
        return new Friendship(id, userId1, userId2, false, createdAt, LocalDateTime.now());
    }

    public Friendship reactivate() {
        return new Friendship(id, userId1, userId2, true, createdAt, LocalDateTime.now());
    }

    public boolean involves(String userId) {
        return userId.equals(userId1) || userId.equals(userId2);
    }

    public String getOtherUserId(String myUserId) {
        if (myUserId.equals(userId1)) return userId2;
        if (myUserId.equals(userId2)) return userId1;
        throw new IllegalArgumentException("User is not part of this friendship");
    }
}
