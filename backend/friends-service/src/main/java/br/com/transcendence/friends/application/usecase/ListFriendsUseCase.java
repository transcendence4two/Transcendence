package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

import java.util.List;

@ApplicationScoped
public class ListFriendsUseCase {

    @Inject
    IFriendshipRepository friendshipRepository;

    public List<Friendship> execute(String userId) {
        return friendshipRepository.findActiveFriendsByUserId(userId);
    }
}
