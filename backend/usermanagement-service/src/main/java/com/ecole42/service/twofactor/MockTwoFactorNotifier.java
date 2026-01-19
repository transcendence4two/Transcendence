package com.ecole42.service.twofactor;

import com.ecole42.domain.entity.User;
import jakarta.enterprise.context.ApplicationScoped;
import org.jboss.logging.Logger;

@ApplicationScoped
public class MockTwoFactorNotifier implements TwoFactorNotifier {
    private static final Logger log = Logger.getLogger(MockTwoFactorNotifier.class);

    @Override
    public void sendCode(User user, String code) {
        log.infof("Mock 2FA code %s sent to user %s (%s)", code, user.username, user.email);
    }
}
