package com.ecole42.service.twofactor;

import com.ecole42.domain.entity.User;

public interface TwoFactorNotifier {
    void sendCode(User user, String code);
}
