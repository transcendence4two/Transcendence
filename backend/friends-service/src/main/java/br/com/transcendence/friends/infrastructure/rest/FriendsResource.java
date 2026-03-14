package br.com.transcendence.friends.infrastructure.rest;

import br.com.transcendence.friends.application.dto.PaginatedResponse;
import br.com.transcendence.friends.application.usecase.ListFriendsUseCase;
import br.com.transcendence.friends.application.usecase.RemoveFriendUseCase;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.model.Page;
import br.com.transcendence.friends.infrastructure.rest.util.UserContextHelper;
import jakarta.inject.Inject;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

@Path("/friends")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class FriendsResource {

    @Inject
    ListFriendsUseCase listFriendsUseCase;

    @Inject
    RemoveFriendUseCase removeFriendUseCase;

    @GET
    public Response listFriends(
            @HeaderParam("X-User-Id") String currentUserId,
            @QueryParam("page") @DefaultValue("1") int page,
            @QueryParam("page_size") @DefaultValue("10") int pageSize) {
        String userId = UserContextHelper.extractUserId(currentUserId);
        Page<Friendship> friendsPage = listFriendsUseCase.execute(userId, page, pageSize);
        return Response.ok(PaginatedResponse.fromPage(friendsPage)).build();
    }

    @DELETE
    @Path("/user/{friendUserId}")
    public Response removeFriend(
            @PathParam("friendUserId") String friendUserId,
            @HeaderParam("X-User-Id") String currentUserId) {
        String userId = UserContextHelper.extractUserId(currentUserId);
        removeFriendUseCase.execute(userId, friendUserId);
        return Response.noContent().build();
    }
}

