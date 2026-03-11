package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class ListFriendsUseCase {

    @Inject
    IFriendshipRepository friendshipRepository;

    public Page<Friendship> execute(String userId, int page, int pageSize) {
        return friendshipRepository.findActiveFriendsByUserId(userId, page, pageSize);
    }
}
