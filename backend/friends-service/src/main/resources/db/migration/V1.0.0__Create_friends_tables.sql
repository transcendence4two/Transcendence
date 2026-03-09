CREATE TABLE friend_requests (
    id UUID PRIMARY KEY,
    requester_id VARCHAR(255) NOT NULL,
    receiver_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE TABLE friendships (
    id UUID PRIMARY KEY,
    user_id_1 VARCHAR(255) NOT NULL,
    user_id_2 VARCHAR(255) NOT NULL,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP
);

CREATE INDEX idx_friend_requests_requester ON friend_requests(requester_id);
CREATE INDEX idx_friend_requests_receiver ON friend_requests(receiver_id);
CREATE INDEX idx_friendships_user_1 ON friendships(user_id_1);
CREATE INDEX idx_friendships_user_2 ON friendships(user_id_2);
CREATE UNIQUE INDEX idx_unique_pending_request ON friend_requests (requester_id, receiver_id) WHERE status = 'PENDING';
