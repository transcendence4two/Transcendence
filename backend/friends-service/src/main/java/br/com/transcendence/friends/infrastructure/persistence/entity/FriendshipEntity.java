package br.com.transcendence.friends.infrastructure.persistence.entity;

import br.com.transcendence.friends.domain.model.Friendship;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "friendships")
public class FriendshipEntity {
    @Id
    private UUID id;

    @Column(name = "user_id_1")
    private String userId1;

    @Column(name = "user_id_2")
    private String userId2;

    private boolean active;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;

    public FriendshipEntity() {}

    public Friendship toDomain() {
        return new Friendship(id, userId1, userId2, active, createdAt, updatedAt);
    }

    public static FriendshipEntity fromDomain(Friendship model) {
        FriendshipEntity entity = new FriendshipEntity();
        entity.id = model.id();
        entity.userId1 = model.userId1();
        entity.userId2 = model.userId2();
        entity.active = model.active();
        entity.createdAt = model.createdAt();
        entity.updatedAt = model.updatedAt();
        return entity;
    }
}
