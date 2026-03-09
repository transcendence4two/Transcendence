package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.RequestStatus;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.List;

@ApplicationScoped
public class ListPendingRequestsUseCase {

    @Inject
    IFriendRequestRepository friendRequestRepository;

    public List<FriendRequest> execute(String receiverId) {
        return friendRequestRepository.findByReceiverAndStatus(receiverId, RequestStatus.PENDING);
    }
}
