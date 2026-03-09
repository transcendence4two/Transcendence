package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.domain.exception.FriendRequestAlreadyExistsException;
import br.com.transcendence.friends.domain.exception.FriendshipAlreadyExistsException;
import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.repository.IFriendRequestRepository;
import br.com.transcendence.friends.domain.repository.IFriendshipRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import static org.mockito.Mockito.*;
import org.mockito.MockitoAnnotations;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;

class SendFriendRequestUseCaseTest {

    @Mock
    IFriendRequestRepository friendRequestRepository;

    @Mock
    IFriendshipRepository friendshipRepository;

    @InjectMocks
    SendFriendRequestUseCase useCase;

    @BeforeEach
    void setUp() {
        MockitoAnnotations.openMocks(this);
    }

    @Test
    void shouldSendRequestSuccessfully() {
        when(friendshipRepository.findByUsers("userA", "userB")).thenReturn(Optional.empty());
        when(friendRequestRepository.findPendingRequest("userA", "userB")).thenReturn(Optional.empty());
        when(friendRequestRepository.findPendingRequest("userB", "userA")).thenReturn(Optional.empty());
        
        when(friendRequestRepository.save(any(FriendRequest.class))).thenAnswer(i -> i.getArguments()[0]);

        FriendRequest result = useCase.execute("userA", "userB");

        assertNotNull(result);
        assertEquals("userA", result.getRequesterId());
        assertEquals("userB", result.getReceiverId());
    }

    @Test
    void shouldThrowWhenAlreadyFriends() {
        Friendship fs = Friendship.create("userA", "userB");
        when(friendshipRepository.findByUsers("userA", "userB")).thenReturn(Optional.of(fs));

        assertThrows(FriendshipAlreadyExistsException.class, () -> useCase.execute("userA", "userB"));
    }

    @Test
    void shouldThrowWhenPendingRequestExistsFromMe() {
        when(friendshipRepository.findByUsers("userA", "userB")).thenReturn(Optional.empty());
        FriendRequest req = FriendRequest.create("userA", "userB");
        when(friendRequestRepository.findPendingRequest("userA", "userB")).thenReturn(Optional.of(req));

        assertThrows(FriendRequestAlreadyExistsException.class, () -> useCase.execute("userA", "userB"));
    }
}
