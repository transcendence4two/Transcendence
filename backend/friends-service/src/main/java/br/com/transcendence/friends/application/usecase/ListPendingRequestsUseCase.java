package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.domain.model.RequestStatus;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class ListPendingRequestsUseCase {

    @Inject
    IFriendRequestRepository friendRequestRepository;

    public Page<FriendRequest> execute(String receiverId, int page, int pageSize) {
        return friendRequestRepository.findByReceiverAndStatus(receiverId, RequestStatus.PENDING, page, pageSize);
    }
}
