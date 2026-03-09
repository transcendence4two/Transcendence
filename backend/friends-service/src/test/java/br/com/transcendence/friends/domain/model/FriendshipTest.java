package br.com.transcendence.friends.domain.model;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FriendshipTest {

    @Test
    void shouldCreateFriendship() {
        Friendship fs = Friendship.create("user1", "user2");
        assertNotNull(fs.getId());
        // Since we order them
        assertEquals("user1", fs.getUserId1());
        assertEquals("user2", fs.getUserId2());
        assertTrue(fs.isActive());
    }

    @Test
    void shouldNotCreateFriendshipToSelf() {
        assertThrows(IllegalArgumentException.class, () -> Friendship.create("user1", "user1"));
    }

    @Test
    void shouldDeactivateFriendship() {
        Friendship fs = Friendship.create("user1", "user2");
        fs.deactivate();
        assertFalse(fs.isActive());
    }
}
