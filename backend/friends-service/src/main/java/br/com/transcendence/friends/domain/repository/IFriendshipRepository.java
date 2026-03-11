package br.com.transcendence.friends.domain.repository;

import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.model.Page;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface IFriendshipRepository {
    Friendship save(Friendship friendship);
    Optional<Friendship> findFriendshipById(UUID id);
    Optional<Friendship> findByUsers(String userId1, String userId2);
    Page<Friendship> findActiveFriendsByUserId(String userId, int page, int pageSize);
}
