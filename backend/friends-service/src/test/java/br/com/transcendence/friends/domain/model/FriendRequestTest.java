package br.com.transcendence.friends.domain.model;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FriendRequestTest {

    @Test
    void shouldCreatePendingRequest() {
        FriendRequest request = FriendRequest.create("user1", "user2");
        
        assertNotNull(request.id());
        assertEquals("user1", request.requesterId());
        assertEquals("user2", request.receiverId());
        assertEquals(RequestStatus.PENDING, request.status());
    }

    @Test
    void shouldNotCreateRequestToSelf() {
        assertThrows(IllegalArgumentException.class, () -> {
            FriendRequest.create("user1", "user1");
        });
    }

    @Test
    void shouldAcceptPendingRequest() {
        FriendRequest request = FriendRequest.create("user1", "user2");
        request = request.accept();
        assertEquals(RequestStatus.ACCEPTED, request.status());
    }

    @Test
    void shouldNotAcceptAlreadyAcceptedRequest() {
        FriendRequest request = FriendRequest.create("user1", "user2");
        final FriendRequest r1 = request.accept();
        assertThrows(IllegalStateException.class, r1::accept);
    }
}
