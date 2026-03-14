package br.com.transcendence.friends.application.usecase;

import br.com.transcendence.friends.application.port.out.UserManagementPort;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.inject.Inject;

@ApplicationScoped
public class FindUserByUsernameUseCase {

    @Inject
    UserManagementPort userManagementPort;

    public Object execute(String username) {
        return userManagementPort.findByUsername(username);
    }
}
