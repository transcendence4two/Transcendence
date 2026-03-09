package br.com.transcendence.friends.infrastructure.rest.exception;

import br.com.transcendence.friends.domain.exception.DomainException;
import br.com.transcendence.friends.domain.exception.FriendRequestNotFoundException;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.util.Map;

@Provider
public class DomainExceptionHandler implements ExceptionMapper<DomainException> {

    @Override
    public Response toResponse(DomainException e) {
        int status = Response.Status.BAD_REQUEST.getStatusCode();
        
        if (e instanceof FriendRequestNotFoundException) {
            status = Response.Status.NOT_FOUND.getStatusCode();
        }

        return Response.status(status)
                .entity(Map.of("error", e.getMessage()))
                .build();
    }
}
