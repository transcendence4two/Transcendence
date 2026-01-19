package com.ecole42.exception;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.ConstraintViolationException;
import jakarta.ws.rs.core.MediaType;
import jakarta.ws.rs.core.Response;
import jakarta.ws.rs.ext.ExceptionMapper;
import jakarta.ws.rs.ext.Provider;
import org.jboss.logging.Logger;

import java.util.HashMap;
import java.util.Map;
import java.util.stream.Collectors;

@Provider
public class GlobalExceptionHandler implements ExceptionMapper<Exception> {
    
    private static final Logger log = Logger.getLogger(GlobalExceptionHandler.class);
    
    @Override
    public Response toResponse(Exception exception) {
        
        if (exception instanceof UserAlreadyExistsException) {
            return buildResponse(
                Response.Status.CONFLICT,
                exception.getMessage()
            );
        }

        if (exception instanceof InvalidCredentialsException) {
            return buildResponse(
                Response.Status.UNAUTHORIZED,
                "Invalid email or password"
            );
        }
        
        if (exception instanceof ConstraintViolationException) {
            ConstraintViolationException cve = (ConstraintViolationException) exception;
            String details = cve.getConstraintViolations().stream()
                .map(ConstraintViolation::getMessage)
                .collect(Collectors.joining(", "));
            
            return buildResponse(
                Response.Status.BAD_REQUEST,
                "Validation failed: " + details
            );
        }
        
        log.error("Unexpected internal error", exception);
        return buildResponse(
            Response.Status.INTERNAL_SERVER_ERROR,
            "Internal server error"
        );
    }
    
    private Response buildResponse(Response.Status status, String message) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("error", message);
        
        return Response
            .status(status)
            .entity(errorResponse)
            .type(MediaType.APPLICATION_JSON)
            .build();
    }
}
