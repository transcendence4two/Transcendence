package com.ecole42.domain.entity;

import io.quarkus.hibernate.orm.panache.PanacheEntityBase;
import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "users")
public class User extends PanacheEntityBase {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Long id;
    
    @Column(unique = true, nullable = false, length = 50)
    public String username;
    
    @Column(unique = true, nullable = false, length = 100)
    public String email;

    @Column(nullable = false)
    public String password;
    
    @Column(name = "two_factor_enabled", nullable = false)
    public Boolean twoFactorEnabled = false;
    
    @Column(name = "profile_picture_url", length = 500)
    public String profilePictureUrl;

    @Column(name = "created_at", nullable = false, updatable = false)
    public LocalDateTime createdAt;
    
    @Column(name = "updated_at")
    public LocalDateTime updatedAt;
    
    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }
    
    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
