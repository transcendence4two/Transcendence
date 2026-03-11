package br.com.transcendence.friends.domain.model;

import java.util.List;

public record Page<T>(
    List<T> items,
    long total,
    int page,
    int pageSize,
    int totalPages
) {
}
