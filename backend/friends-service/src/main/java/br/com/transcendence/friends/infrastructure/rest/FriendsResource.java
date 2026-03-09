package br.com.transcendence.friends.infrastructure.rest;

import br.com.transcendence.friends.application.usecase.ListFriendsUseCase;
import br.com.transcendence.friends.application.usecase.RemoveFriendUseCase;
import br.com.transcendence.friends.domain.model.Friendship;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.List;

@Path("/friends")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class FriendsResource {

    @Inject
    ListFriendsUseCase listFriendsUseCase;

    @Inject
    RemoveFriendUseCase removeFriendUseCase;

    private String getCurrentUserId(String headerUserId) {
        if (headerUserId == null || headerUserId.isBlank()) {
            throw new NotAuthorizedException("X-User-Id header is required for context");
        }
        return headerUserId;
    }

    @GET
    public Response listFriends(@HeaderParam("X-User-Id") String currentUserId) {
        String userId = getCurrentUserId(currentUserId);
        List<Friendship> friends = listFriendsUseCase.execute(userId);
        return Response.ok(friends).build();
    }

    @DELETE
    @Path("/user/{friendUserId}")
    @Transactional
    public Response removeFriend(@PathParam("friendUserId") String friendUserId, @HeaderParam("X-User-Id") String currentUserId) {
        String userId = getCurrentUserId(currentUserId);
        removeFriendUseCase.execute(userId, friendUserId);
        return Response.noContent().build();
    }
}
