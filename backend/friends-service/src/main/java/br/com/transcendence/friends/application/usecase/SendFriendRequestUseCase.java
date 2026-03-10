package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.application.port.out.UserManagementPort;
import br.com.transcendence.friends.domain.exception.FriendRequestAlreadyExistsException;
import br.com.transcendence.friends.domain.exception.FriendshipAlreadyExistsException;
import br.com.transcendence.friends.domain.exception.UserNotFoundException;
import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.Optional;

@ApplicationScoped
public class SendFriendRequestUseCase {

    @Inject
    IFriendRequestRepository friendRequestRepository;

    @Inject
    IFriendshipRepository friendshipRepository;

    @Inject
    UserManagementPort userManagementPort;

    public FriendRequest execute(String requesterId, String receiverId) {
        if (requesterId == null || receiverId == null || requesterId.equals(receiverId)) {
            throw new IllegalArgumentException("Invalid requester or receiver ID");
        }

        if (!userManagementPort.userExists(receiverId)) {
            throw new UserNotFoundException(receiverId);
        }

        Optional<Friendship> existingFriendship = friendshipRepository.findByUsers(requesterId, receiverId);
        if (existingFriendship.isPresent() && existingFriendship.get().active()) {
            throw new FriendshipAlreadyExistsException("Users are already friends");
        }

        Optional<FriendRequest> pendingreq1 = friendRequestRepository.findPendingRequest(requesterId, receiverId);
        if (pendingreq1.isPresent()) {
            throw new FriendRequestAlreadyExistsException("A pending friend request already exists between these users");
        }
        Optional<FriendRequest> pendingreq2 = friendRequestRepository.findPendingRequest(receiverId, requesterId);
        if (pendingreq2.isPresent()) {
            throw new FriendRequestAlreadyExistsException("Receiver has already sent you a friend request. You can accept it instead.");
        }

        FriendRequest request = FriendRequest.create(requesterId, receiverId);
        return friendRequestRepository.save(request);
    }
}
