package br.com.transcendence.friends.domain.model;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

class FriendRequestTest {

    @Test
    void shouldCreatePendingRequest() {
        FriendRequest request = FriendRequest.create("user1", "user2");
        
        assertNotNull(request.getId());
        assertEquals("user1", request.getRequesterId());
        assertEquals("user2", request.getReceiverId());
        assertEquals(RequestStatus.PENDING, request.getStatus());
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
        request.accept();
        assertEquals(RequestStatus.ACCEPTED, request.getStatus());
    }

    @Test
    void shouldNotAcceptAlreadyAcceptedRequest() {
        FriendRequest request = FriendRequest.create("user1", "user2");
        request.accept();
        assertThrows(IllegalStateException.class, request::accept);
    }
}
