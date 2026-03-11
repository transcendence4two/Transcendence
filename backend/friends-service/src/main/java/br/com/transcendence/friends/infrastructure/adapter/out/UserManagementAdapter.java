package br.com.transcendence.friends.infrastructure.adapter.out;

import br.com.transcendence.friends.application.port.out.UserManagementPort;
import br.com.transcendence.friends.infrastructure.client.IUserManagementClient;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.WebApplicationException;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@ApplicationScoped
public class UserManagementAdapter implements UserManagementPort {

    @Inject
    @RestClient
    IUserManagementClient userManagementClient;

    @Override
    public boolean userExists(String userId) {
        try (Response response = userManagementClient.findById(userId)) {
            return response.getStatus() == Response.Status.OK.getStatusCode();
        } catch (WebApplicationException e) {
            if (e.getResponse().getStatus() == Response.Status.NOT_FOUND.getStatusCode()) {
                return false;
            }
            throw e;
        }
    }

    @Override
    public Object findByUsername(String username) {
        try (Response response = userManagementClient.findByUsername(username)) {
            if (response.getStatus() == Response.Status.OK.getStatusCode()) {
                return response.readEntity(Object.class);
            }
            throw new RuntimeException("User not found or error from user management: " + response.getStatus());
        }
    }
}

