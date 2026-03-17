package br.com.transcendence.friends.infrastructure.rest.filter;

import jakarta.annotation.Priority;
import jakarta.ws.rs.Priorities;
import jakarta.ws.rs.container.ContainerRequestContext;
import jakarta.ws.rs.container.ContainerRequestFilter;
import jakarta.ws.rs.container.ContainerResponseContext;
import jakarta.ws.rs.container.ContainerResponseFilter;
import jakarta.ws.rs.ext.Provider;
import org.jboss.logging.MDC;

import java.util.Optional;
import java.util.UUID;

@Provider
@Priority(Priorities.USER - 100)
public class RequestContextFilter implements ContainerRequestFilter, ContainerResponseFilter {

    @Override
    public void filter(ContainerRequestContext ctx) {
        String requestId = Optional.ofNullable(ctx.getHeaderString("X-Request-ID"))
                .orElse(UUID.randomUUID().toString());
        String traceId = Optional.ofNullable(ctx.getHeaderString("X-Trace-ID"))
                .orElse(requestId);

        MDC.put("http.request.id", requestId);
        MDC.put("trace.id", traceId);
        MDC.put("http.request.method", ctx.getMethod());
        MDC.put("url.path", ctx.getUriInfo().getRequestUri().getPath());
        MDC.put("url.route", ctx.getUriInfo().getPath());
        MDC.put("user_agent.original", ctx.getHeaderString("User-Agent"));

        String userId = ctx.getHeaderString("X-User-Id");
        if (userId != null && !userId.isBlank()) {
            MDC.put("user.id", userId);
        }
    }

    @Override
    public void filter(ContainerRequestContext req, ContainerResponseContext res) {
        MDC.put("http.response.status_code", String.valueOf(res.getStatus()));
        MDC.clear();
    }
}
