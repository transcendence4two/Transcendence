package com.ecole42.domain.repository;

import com.ecole42.domain.entity.User;
import io.quarkus.hibernate.orm.panache.PanacheRepository;
import jakarta.enterprise.context.ApplicationScoped;
import java.util.Optional;

@ApplicationScoped
public class UserRepository implements PanacheRepository<User> {
    
    public Optional<User> findByEmail(String email) {
        return find("email", email).firstResultOptional();
    }
    
    public Optional<User> findByUsername(String username) {
        return find("username", username).firstResultOptional();
    }
}
