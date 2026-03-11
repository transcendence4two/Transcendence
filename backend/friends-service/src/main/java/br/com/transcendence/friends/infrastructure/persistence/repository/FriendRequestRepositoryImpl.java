package br.com.transcendence.friends.infrastructure.persistence.repository;

import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.domain.model.RequestStatus;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import br.com.transcendence.friends.infrastructure.persistence.entity.FriendRequestEntity;
import br.com.transcendence.friends.infrastructure.persistence.util.PaginationHelper;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class FriendRequestRepositoryImpl implements IFriendRequestRepository, PanacheRepositoryBase<FriendRequestEntity, UUID> {

    @Override
    public FriendRequest save(FriendRequest friendRequest) {
        FriendRequestEntity entity = FriendRequestEntity.fromDomain(friendRequest);
        getEntityManager().merge(entity);
        return friendRequest;
    }

    @Override
    public Optional<FriendRequest> findRequestById(UUID id) {
        return find("id", id).firstResultOptional().map(FriendRequestEntity::toDomain);
    }

    @Override
    public Optional<FriendRequest> findPendingRequest(String requesterId, String receiverId) {
        return find("requesterId = ?1 and receiverId = ?2 and status = ?3", requesterId, receiverId, RequestStatus.PENDING)
                .firstResultOptional()
                .map(FriendRequestEntity::toDomain);
    }

    @Override
    public Page<FriendRequest> findByReceiverAndStatus(String receiverId, RequestStatus status, int page, int pageSize) {
        return PaginationHelper.paginate(
                find("receiverId = ?1 and status = ?2", receiverId, status),
                page, pageSize, FriendRequestEntity::toDomain);
    }
}
