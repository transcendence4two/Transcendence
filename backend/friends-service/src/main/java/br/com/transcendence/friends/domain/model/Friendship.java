package br.com.transcendence.friends.domain.model;

import java.time.LocalDateTime;
import java.util.UUID;

public class Friendship {
    private UUID id;
    private String userId1;
    private String userId2;
    private boolean active;
    private LocalDateTime createdAt;
    private LocalDateTime updatedAt;

    public Friendship(UUID id, String userId1, String userId2, boolean active, LocalDateTime createdAt, LocalDateTime updatedAt) {
        this.id = id;
        this.userId1 = userId1;
        this.userId2 = userId2;
        this.active = active;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

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

    public void deactivate() {
        this.active = false;
        this.updatedAt = LocalDateTime.now();
    }

    public void reactivate() {
        this.active = true;
        this.updatedAt = LocalDateTime.now();
    }

    public boolean involves(String userId) {
        return userId.equals(userId1) || userId.equals(userId2);
    }

    public String getOtherUserId(String myUserId) {
        if (myUserId.equals(userId1)) return userId2;
        if (myUserId.equals(userId2)) return userId1;
        throw new IllegalArgumentException("User is not part of this friendship");
    }

    // Getters and Setters
    public UUID getId() { return id; }
    public String getUserId1() { return userId1; }
    public String getUserId2() { return userId2; }
    public boolean isActive() { return active; }
    public LocalDateTime getCreatedAt() { return createdAt; }
    public LocalDateTime getUpdatedAt() { return updatedAt; }

    public void setId(UUID id) { this.id = id; }
    public void setUserId1(String userId1) { this.userId1 = userId1; }
    public void setUserId2(String userId2) { this.userId2 = userId2; }
    public void setActive(boolean active) { this.active = active; }
    public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
}
