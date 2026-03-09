package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.exception.DomainException;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.Optional;

@ApplicationScoped
public class RemoveFriendUseCase {

    @Inject
    IFriendshipRepository friendshipRepository;

    public void execute(String currentUserId, String friendUserId) {
        Optional<Friendship> optFriendship = friendshipRepository.findByUsers(currentUserId, friendUserId);

        if (optFriendship.isEmpty() || !optFriendship.get().isActive()) {
            throw new DomainException("Active friendship not found");
        }

        Friendship friendship = optFriendship.get();
        friendship.deactivate();
        friendshipRepository.save(friendship);
    }
}
