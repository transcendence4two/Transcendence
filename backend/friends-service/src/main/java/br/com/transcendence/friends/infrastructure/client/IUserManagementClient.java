package br.com.transcendence.friends.infrastructure.client;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.annotation.RegisterClientHeaders;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@Path("/users")
@RegisterRestClient(configKey = "usermanagement-client")
@RegisterClientHeaders(HeaderPropagationFactory.class)
public interface IUserManagementClient {

    @GET
    @Path("/find-by-username/{username}")
    Response findByUsername(@PathParam("username") String username);

    @GET
    @Path("/{id}")
    Response findById(@PathParam("id") String id);
}
