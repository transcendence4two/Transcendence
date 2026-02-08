package emails.service.transcendence.infrastructure

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Configuration
import org.springframework.data.redis.connection.RedisConnectionFactory
import org.springframework.data.redis.listener.PatternTopic
import org.springframework.data.redis.listener.RedisMessageListenerContainer
import org.springframework.beans.factory.annotation.Value

@Configuration
class RedisConfig(
    @Value("\${redis.queue.name:email-queue}")
    private val queueName: String
) {
    
    @Bean
    fun redisMessageListenerContainer(
        connectionFactory: RedisConnectionFactory,
        emailListener: EmailListener
    ): RedisMessageListenerContainer {
        val container = RedisMessageListenerContainer()
        container.setConnectionFactory(connectionFactory)
        container.addMessageListener(emailListener, PatternTopic(queueName))
        return container
    }
}
