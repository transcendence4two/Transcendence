package br.com.transcendence.friends.domain.repository;

import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.domain.model.RequestStatus;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface IFriendRequestRepository {
    FriendRequest save(FriendRequest friendRequest);
    Optional<FriendRequest> findRequestById(UUID id);
    Optional<FriendRequest> findPendingRequest(String requesterId, String receiverId);
    Page<FriendRequest> findByReceiverAndStatus(String receiverId, RequestStatus status, int page, int pageSize);
}
