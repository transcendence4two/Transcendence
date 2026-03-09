package br.com.transcendence.friends.domain.repository;

import br.com.transcendence.friends.domain.model.Friendship;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface IFriendshipRepository {
    Friendship save(Friendship friendship);
    Optional<Friendship> findFriendshipById(UUID id);
    Optional<Friendship> findByUsers(String userId1, String userId2);
    List<Friendship> findActiveFriendsByUserId(String userId);
}
