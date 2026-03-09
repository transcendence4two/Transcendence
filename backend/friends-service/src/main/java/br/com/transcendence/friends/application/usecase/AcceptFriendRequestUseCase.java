package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.exception.FriendRequestNotFoundException;
import br.com.transcendence.friends.domain.exception.FriendshipAlreadyExistsException;
import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.Optional;
import java.util.UUID;

@ApplicationScoped
public class AcceptFriendRequestUseCase {

    @Inject
    IFriendRequestRepository friendRequestRepository;

    @Inject
    IFriendshipRepository friendshipRepository;

    public Friendship execute(UUID requestId, String currentUserId) {
        FriendRequest request = friendRequestRepository.findRequestById(requestId)
                .orElseThrow(() -> new FriendRequestNotFoundException(requestId));

        if (!request.receiverId().equals(currentUserId)) {
            throw new IllegalArgumentException("Only the receiver can accept the friend request");
        }

        request = request.accept();
        friendRequestRepository.save(request);

        Optional<Friendship> existingFriendship = friendshipRepository.findByUsers(request.requesterId(), request.receiverId());
        
        if (existingFriendship.isPresent()) {
            Friendship friendship = existingFriendship.get();
            if (friendship.active()) {
                throw new FriendshipAlreadyExistsException("Users are already friends");
            }
            friendship = friendship.reactivate();
            return friendshipRepository.save(friendship);
        }
        Friendship newFriendship = Friendship.create(request.requesterId(), request.receiverId());
        return friendshipRepository.save(newFriendship);
    }
}
