package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.exception.FriendRequestNotFoundException;
import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.UUID;

@ApplicationScoped
public class RejectFriendRequestUseCase {

    @Inject
    IFriendRequestRepository friendRequestRepository;

    public void execute(UUID requestId, String currentUserId) {
        FriendRequest request = friendRequestRepository.findRequestById(requestId)
                .orElseThrow(() -> new FriendRequestNotFoundException(requestId));

        if (!request.receiverId().equals(currentUserId)) {
            throw new IllegalArgumentException("Only the receiver can reject the friend request");
        }

        request = request.reject();
        friendRequestRepository.save(request);
    }
}
