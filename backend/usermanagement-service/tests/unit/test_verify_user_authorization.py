import pytest

from src.core.auth import verify_user_authorization
from src.domain.exceptions import UnauthorizedActionError


class TestVerifyUserAuthorization:
    """Unit tests for verify_user_authorization function"""

    def test_allows_when_user_id_matches_token_subject(self):
        payload = {"sub": "user-123", "iss": "usermanagement"}

        # Should not raise
        verify_user_authorization("user-123", payload)

    def test_raises_when_user_id_does_not_match_token_subject(self):
        payload = {"sub": "user-123", "iss": "usermanagement"}

        with pytest.raises(UnauthorizedActionError) as exc_info:
            verify_user_authorization("user-456", payload)

        assert "not authorized" in str(exc_info.value).lower()

    def test_raises_when_trying_to_access_different_user(self):
        payload = {"sub": "alice-id", "iss": "usermanagement"}

        with pytest.raises(UnauthorizedActionError):
            verify_user_authorization("bob-id", payload)

    def test_allows_access_to_own_resource(self):
        user_id = "my-unique-id-123"
        payload = {"sub": user_id, "iss": "usermanagement"}

        # Should not raise - user accessing their own resource
        verify_user_authorization(user_id, payload)

    def test_raises_with_empty_user_id(self):
        payload = {"sub": "user-123", "iss": "usermanagement"}

        with pytest.raises(UnauthorizedActionError):
            verify_user_authorization("", payload)

    def test_raises_when_token_subject_is_none(self):
        payload = {"sub": None, "iss": "usermanagement"}

        with pytest.raises(UnauthorizedActionError):
            verify_user_authorization("user-123", payload)

    def test_raises_when_token_has_no_subject(self):
        payload = {"iss": "usermanagement"}

        with pytest.raises(UnauthorizedActionError):
            verify_user_authorization("user-123", payload)

    def test_case_sensitive_comparison(self):
        payload = {"sub": "User-123", "iss": "usermanagement"}

        # Should raise because IDs are case-sensitive
        with pytest.raises(UnauthorizedActionError):
            verify_user_authorization("user-123", payload)
