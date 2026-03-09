package br.com.transcendence.friends.infrastructure.persistence.repository;

import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.RequestStatus;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import br.com.transcendence.friends.infrastructure.persistence.entity.FriendRequestEntity;
import io.quarkus.hibernate.orm.panache.PanacheRepositoryBase;
import jakarta.enterprise.context.ApplicationScoped;

import java.util.List;
import java.util.Optional;
import java.util.UUID;
import java.util.stream.Collectors;

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
    public List<FriendRequest> findByReceiverAndStatus(String receiverId, RequestStatus status) {
        return find("receiverId = ?1 and status = ?2", receiverId, status)
                .stream()
                .map(FriendRequestEntity::toDomain)
                .collect(Collectors.toList());
    }
}
