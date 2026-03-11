package br.com.transcendence.friends.infrastructure.persistence.repository;

import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import br.com.transcendence.friends.infrastructure.persistence.entity.FriendshipEntity;
import io.quarkus.hibernate.orm.panache.PanacheQuery;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

@ApplicationScoped
public class FriendshipRepositoryImpl implements IFriendshipRepository, PanacheRepositoryBase<FriendshipEntity, UUID> {

    @Override
    public Friendship save(Friendship friendship) {
        FriendshipEntity entity = FriendshipEntity.fromDomain(friendship);
        getEntityManager().merge(entity);
        return friendship;
    }

    @Override
    public Optional<Friendship> findFriendshipById(UUID id) {
        return find("id", id).firstResultOptional().map(FriendshipEntity::toDomain);
    }

    @Override
    public Optional<Friendship> findByUsers(String userId1, String userId2) {
        String u1 = userId1.compareTo(userId2) < 0 ? userId1 : userId2;
        String u2 = userId1.compareTo(userId2) < 0 ? userId2 : userId1;

        return find("userId1 = ?1 and userId2 = ?2", u1, u2)
                .firstResultOptional()
                .map(FriendshipEntity::toDomain);
    }

    @Override
    public Page<Friendship> findActiveFriendsByUserId(String userId, int page, int pageSize) {
        PanacheQuery<FriendshipEntity> query = find("(userId1 = ?1 or userId2 = ?1) and active = true", userId);
        
        long total = query.count();
        List<Friendship> items = query.page(io.quarkus.panache.common.Page.of(page - 1, pageSize))
                .stream()
                .map(FriendshipEntity::toDomain)
                .collect(Collectors.toList());
        
        int totalPages = (int) Math.ceil((double) total / pageSize);

        return new Page<>(items, total, page, pageSize, totalPages);
    }
}
