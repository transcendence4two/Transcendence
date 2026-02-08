package emails.service.transcendence.infrastructure

import emails.service.transcendence.application.EmailService
import emails.service.transcendence.domain.EmailMessage
import com.fasterxml.jackson.databind.ObjectMapper
import org.springframework.data.redis.connection.Message
import org.springframework.data.redis.connection.MessageListener
import org.springframework.stereotype.Component
import org.slf4j.LoggerFactory

@Component
class EmailListener(
    private val emailService: EmailService,
    private val objectMapper: ObjectMapper
) : MessageListener {
    private val logger = LoggerFactory.getLogger(EmailListener::class.java)

    override fun onMessage(message: Message, pattern: ByteArray?) {
        try {
            val messageBody = String(message.body)
            logger.info("Received message from Redis: $messageBody")
            
            val emailMessage = objectMapper.readValue(messageBody, EmailMessage::class.java)
            emailService.sendEmail(emailMessage)
        } catch (e: Exception) {
            logger.error("Error processing message from Redis", e)
        }
    }
}
