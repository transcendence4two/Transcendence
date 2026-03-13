package br.com.transcendence.friends.infrastructure.client;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@Path("/")
@RegisterRestClient(configKey = "usermanagement-client")
public interface IUserManagementClient {

    @GET
    @Path("/users/find-by-username/{username}")
    Response findByUsername(@PathParam("username") String username);

    @GET
    @Path("/internal/users/{id}/exists")
    Response findById(@PathParam("id") String id);
}
