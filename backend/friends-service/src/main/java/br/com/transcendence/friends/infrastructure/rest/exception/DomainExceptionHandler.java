package br.com.transcendence.friends.infrastructure.rest.exception;

import br.com.transcendence.friends.domain.exception.DomainException;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import org.jboss.logging.Logger;
import org.jboss.logging.MDC;
import java.util.Map;

@Provider
public class DomainExceptionHandler implements ExceptionMapper<DomainException> {

    private static final Logger LOG = Logger.getLogger(DomainExceptionHandler.class);

    @Override
    public Response toResponse(DomainException e) {
        MDC.put("error_type", e.getClass().getSimpleName());
        MDC.put("exception_class", e.getClass().getSimpleName());
        if (e.httpStatus() >= 500) {
            LOG.errorf("Domain error: %s", e.getMessage());
        } else {
            LOG.warnf("Domain error: %s", e.getMessage());
        }
        MDC.remove("error_type");
        MDC.remove("exception_class");
        return Response.status(e.httpStatus())
                .entity(Map.of("error", e.getMessage()))
                .build();
    }
}

