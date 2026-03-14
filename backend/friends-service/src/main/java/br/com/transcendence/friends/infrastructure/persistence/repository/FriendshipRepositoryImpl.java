package br.com.transcendence.friends.infrastructure.persistence.repository;

import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import br.com.transcendence.friends.infrastructure.persistence.entity.FriendshipEntity;
import br.com.transcendence.friends.infrastructure.persistence.util.PaginationHelper;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.Optional;
import java.util.UUID;

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
        String[] ordered = normalizeUserOrder(userId1, userId2);
        return find("userId1 = ?1 and userId2 = ?2", ordered[0], ordered[1])
                .firstResultOptional()
                .map(FriendshipEntity::toDomain);
    }

    @Override
    public Page<Friendship> findActiveFriendsByUserId(String userId, int page, int pageSize) {
        return PaginationHelper.paginate(
                find("(userId1 = ?1 or userId2 = ?1) and active = true", userId),
                page, pageSize, FriendshipEntity::toDomain);
    }

    private String[] normalizeUserOrder(String userId1, String userId2) {
        if (userId1.compareTo(userId2) <= 0) {
            return new String[]{userId1, userId2};
        }
        return new String[]{userId2, userId1};
    }
}
