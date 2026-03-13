package br.com.transcendence.friends.application.port.out;

public interface UserManagementPort {
    boolean userExists(String userId);
    Object findByUsername(String username);
}
