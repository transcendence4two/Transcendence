package br.com.transcendence.friends.application.dto;

import java.util.List;
import br.com.transcendence.friends.domain.model.Page;

public record PaginatedResponse<T>(
    List<T> items,
    long total,
    int page,
    int page_size,
    int total_pages
) {
    public static <T> PaginatedResponse<T> fromPage(Page<T> domainPage) {
        return new PaginatedResponse<>(
            domainPage.items(),
            domainPage.total(),
            domainPage.page(),
            domainPage.pageSize(),
            domainPage.totalPages()
        );
    }
}
