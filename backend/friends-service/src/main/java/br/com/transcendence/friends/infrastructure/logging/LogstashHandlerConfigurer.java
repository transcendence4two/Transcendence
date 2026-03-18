package br.com.transcendence.friends.infrastructure.logging;

import io.quarkus.runtime.StartupEvent;
import jakarta.enterprise.context.ApplicationScoped;
import jakarta.enterprise.event.Observes;
import org.eclipse.microprofile.config.inject.ConfigProperty;

import java.util.logging.Level;
import java.util.logging.Logger;

@ApplicationScoped
public class LogstashHandlerConfigurer {

    @ConfigProperty(name = "logstash.host", defaultValue = "logstash")
    String host;

    @ConfigProperty(name = "logstash.port", defaultValue = "5000")
    int port;

    @ConfigProperty(name = "logstash.service-name", defaultValue = "friends-service")
    String serviceName;

    @ConfigProperty(name = "logstash.service-environment", defaultValue = "development")
    String serviceEnvironment;

    void onStart(@Observes StartupEvent event) {
        LogstashTcpHandler handler = new LogstashTcpHandler(host, port, serviceName, serviceEnvironment);
        handler.setLevel(Level.INFO);
        Logger.getLogger("").addHandler(handler);
    }
}
