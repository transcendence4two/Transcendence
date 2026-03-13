package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.exception.FriendshipNotFoundException;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;

import java.util.Optional;

@ApplicationScoped
public class RemoveFriendUseCase {

    @Inject
    IFriendshipRepository friendshipRepository;

    @Transactional
    public void execute(String currentUserId, String friendUserId) {
        Optional<Friendship> optFriendship = friendshipRepository.findByUsers(currentUserId, friendUserId);

        if (optFriendship.isEmpty() || !optFriendship.get().active()) {
            throw new FriendshipNotFoundException(currentUserId, friendUserId);
        }

        Friendship friendship = optFriendship.get().deactivate();
        friendshipRepository.save(friendship);
    }
}
