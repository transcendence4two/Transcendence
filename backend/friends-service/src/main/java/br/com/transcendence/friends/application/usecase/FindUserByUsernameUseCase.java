package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.infrastructure.client.IUserManagementClient;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@ApplicationScoped
public class FindUserByUsernameUseCase {

    @Inject
    @RestClient
    IUserManagementClient userManagementClient;

    public Object execute(String username) {
        try (Response response = userManagementClient.findByUsername(username)) {
            if (response.getStatus() == 200) {
                return response.readEntity(Object.class);
            } else {
                throw new RuntimeException("User not found or error from user management: " + response.getStatus());
            }
        } catch (Exception e) {
            throw new RuntimeException("Failed to find user by username", e);
        }
    }
}
