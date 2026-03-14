package br.com.transcendence.friends.infrastructure.persistence.util;

import br.com.transcendence.friends.domain.model.Page;
import io.quarkus.hibernate.orm.panache.PanacheQuery;

import java.util.List;
import java.util.function.Function;

public final class PaginationHelper {

    private PaginationHelper() {}

    public static <E, D> Page<D> paginate(
            PanacheQuery<E> query, int page, int pageSize, Function<E, D> mapper) {
        long total = query.count();
        List<D> items = query
                .page(io.quarkus.panache.common.Page.of(page - 1, pageSize))
                .stream()
                .map(mapper)
                .toList();
        int totalPages = (int) Math.ceil((double) total / pageSize);
        return new Page<>(items, total, page, pageSize, totalPages);
    }
}
