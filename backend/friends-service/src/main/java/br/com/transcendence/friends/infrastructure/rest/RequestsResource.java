package br.com.transcendence.friends.infrastructure.rest;

import br.com.transcendence.friends.application.dto.PaginatedResponse;
import br.com.transcendence.friends.application.dto.SendRequestDTO;
import br.com.transcendence.friends.application.usecase.AcceptFriendRequestUseCase;
import br.com.transcendence.friends.application.usecase.ListPendingRequestsUseCase;
import br.com.transcendence.friends.application.usecase.RejectFriendRequestUseCase;
import br.com.transcendence.friends.application.usecase.SendFriendRequestUseCase;
import br.com.transcendence.friends.domain.model.FriendRequest;
import br.com.transcendence.friends.domain.model.Friendship;
import br.com.transcendence.friends.domain.model.Page;
import jakarta.inject.Inject;
import jakarta.transaction.Transactional;
import jakarta.ws.rs.*;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;

import java.util.UUID;

@Path("/friends/requests")
@Produces(MediaType.APPLICATION_JSON)
@Consumes(MediaType.APPLICATION_JSON)
public class RequestsResource {

    @Inject
    SendFriendRequestUseCase sendFriendRequestUseCase;

    @Inject
    AcceptFriendRequestUseCase acceptFriendRequestUseCase;

    @Inject
    RejectFriendRequestUseCase rejectFriendRequestUseCase;

    @Inject
    ListPendingRequestsUseCase listPendingRequestsUseCase;

    private String getCurrentUserId(String headerUserId) {
        if (headerUserId == null || headerUserId.isBlank()) {
            throw new NotAuthorizedException("X-User-Id header is required for context");
        }
        return headerUserId;
    }

    @POST
    @Transactional
    public Response sendRequest(@HeaderParam("X-User-Id") String currentUserId, SendRequestDTO dto) {
        String requesterId = getCurrentUserId(currentUserId);
        FriendRequest request = sendFriendRequestUseCase.execute(requesterId, dto.receiverId());
        return Response.status(Response.Status.CREATED).entity(request).build();
    }

    @POST
    @Path("/{requestId}/accept")
    @Transactional
    public Response acceptRequest(@PathParam("requestId") UUID requestId, @HeaderParam("X-User-Id") String currentUserId) {
        String receiverId = getCurrentUserId(currentUserId);
        Friendship friendship = acceptFriendRequestUseCase.execute(requestId, receiverId);
        return Response.ok(friendship).build();
    }

    @POST
    @Path("/{requestId}/reject")
    @Transactional
    public Response rejectRequest(@PathParam("requestId") UUID requestId, @HeaderParam("X-User-Id") String currentUserId) {
        String receiverId = getCurrentUserId(currentUserId);
        rejectFriendRequestUseCase.execute(requestId, receiverId);
        return Response.noContent().build();
    }

    @GET
    public Response listPendingRequests(
            @HeaderParam("X-User-Id") String currentUserId,
            @QueryParam("page") @DefaultValue("1") int page,
            @QueryParam("page_size") @DefaultValue("10") int pageSize) {
        String receiverId = getCurrentUserId(currentUserId);
        Page<FriendRequest> requestsPage = listPendingRequestsUseCase.execute(receiverId, page, pageSize);
        return Response.ok(PaginatedResponse.fromPage(requestsPage)).build();
    }
}
