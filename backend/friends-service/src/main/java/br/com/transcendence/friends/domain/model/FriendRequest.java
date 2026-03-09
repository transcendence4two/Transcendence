package br.com.transcendence.friends.domain.model;

import java.time.LocalDateTime;
import java.util.UUID;

public class FriendRequest {
    private UUID id;
    private String requesterId;
    private String receiverId;
    private RequestStatus status;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public FriendRequest(UUID id, String requesterId, String receiverId, RequestStatus status, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.requesterId = requesterId;
        this.receiverId = receiverId;
        this.status = status;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

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

    public void accept() {
        if (this.status != RequestStatus.PENDING) {
            throw new IllegalStateException("Friend request is not pending");
        }
        this.status = RequestStatus.ACCEPTED;
        this.updatedAt = LocalDateTime.now();
    }

    public void reject() {
        if (this.status != RequestStatus.PENDING) {
            throw new IllegalStateException("Friend request is not pending");
        }
        this.status = RequestStatus.REJECTED;
        this.updatedAt = LocalDateTime.now();
    }

    public UUID getId() { return id; }
    public String getRequesterId() { return requesterId; }
    public String getReceiverId() { return receiverId; }
    public RequestStatus getStatus() { return status; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }

    public void setId(UUID id) { this.id = id; }
    public void setRequesterId(String requesterId) { this.requesterId = requesterId; }
    public void setReceiverId(String receiverId) { this.receiverId = receiverId; }
    public void setStatus(RequestStatus status) { this.status = status; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
