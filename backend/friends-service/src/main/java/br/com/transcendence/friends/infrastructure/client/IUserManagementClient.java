package br.com.transcendence.friends.infrastructure.client;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.PathParam;
import jakarta.ws.rs.core.Response;
import org.eclipse.microprofile.rest.client.annotation.RegisterClientHeaders;
import org.eclipse.microprofile.rest.client.inject.RegisterRestClient;

@RegisterRestClient(configKey = "usermanagement-client")
@RegisterClientHeaders(HeaderPropagationFactory.class)
public interface IUserManagementClient {

    @GET
    @jakarta.ws.rs.Path("/internal/users/{id}/exists")
    Response userExists(@PathParam("id") String id);
}
