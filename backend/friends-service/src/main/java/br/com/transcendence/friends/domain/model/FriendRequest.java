package br.com.transcendence.friends.domain.model;

import java.time.LocalDateTime;
import java.util.UUID;

public record FriendRequest(
    UUID id,
    String requesterId,
    String receiverId,
    RequestStatus status,
    LocalDateTime createdAt,
    LocalDateTime updatedAt
) {
    public static FriendRequest create(String requesterId, String receiverId) {
        if (requesterId.equals(receiverId)) {
            throw new IllegalArgumentException("Cannot send friend request to yourself");
        }
        return new FriendRequest(
            UUID.randomUUID(),
            requesterId,
            receiverId,
            RequestStatus.PENDING,
            LocalDateTime.now(),
            LocalDateTime.now()
        );
    }

    public FriendRequest accept() {
        if (this.status != RequestStatus.PENDING) {
            throw new IllegalStateException("Friend request is not pending");
        }
        return new FriendRequest(id, requesterId, receiverId, RequestStatus.ACCEPTED, createdAt, LocalDateTime.now());
    }

    public FriendRequest reject() {
        if (this.status != RequestStatus.PENDING) {
            throw new IllegalStateException("Friend request is not pending");
        }
        return new FriendRequest(id, requesterId, receiverId, RequestStatus.REJECTED, createdAt, LocalDateTime.now());
    }
}
