package br.com.transcendence.friends.infrastructure.rest.exception;

import br.com.transcendence.friends.domain.exception.DomainException;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import java.util.Map;

@Provider
public class DomainExceptionHandler implements ExceptionMapper<DomainException> {

    @Override
    public Response toResponse(DomainException e) {
        return Response.status(e.httpStatus())
                .entity(Map.of("error", e.getMessage()))
                .build();
    }
}

