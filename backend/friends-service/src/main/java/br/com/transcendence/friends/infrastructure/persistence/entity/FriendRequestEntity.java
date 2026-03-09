package br.com.transcendence.friends.infrastructure.persistence.entity;

import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.RequestStatus;
import jakarta.persistence.*;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "friend_requests")
public class FriendRequestEntity {
    @Id
    public UUID id;

    @Column(name = "requester_id")
    public String requesterId;

    @Column(name = "receiver_id")
    public String receiverId;

    @Enumerated(EnumType.STRING)
    public RequestStatus status;

    @Column(name = "created_at")
    public LocalDateTime createdAt;

    @Column(name = "updated_at")
    public LocalDateTime updatedAt;

    public FriendRequestEntity() {}

    public FriendRequest toDomain() {
        return new FriendRequest(id, requesterId, receiverId, status, createdAt, updatedAt);
    }

    public static FriendRequestEntity fromDomain(FriendRequest model) {
        FriendRequestEntity entity = new FriendRequestEntity();
        entity.id = model.getId();
        entity.requesterId = model.getRequesterId();
        entity.receiverId = model.getReceiverId();
        entity.status = model.getStatus();
        entity.createdAt = model.getCreatedAt();
        entity.updatedAt = model.getUpdatedAt();
        return entity;
    }
}
