package emails.service.transcendence.application

import emails.service.transcendence.domain.EmailMessage
import org.springframework.mail.SimpleMailMessage
import org.springframework.mail.javamail.JavaMailSender
import org.springframework.stereotype.Service
import org.slf4j.LoggerFactory

@Service
class EmailService(
    private val mailSender: JavaMailSender
) {
    private val logger = LoggerFactory.getLogger(EmailService::class.java)

    fun sendEmail(emailMessage: EmailMessage) {
        try {
            val message = SimpleMailMessage()
            message.setTo(emailMessage.email)
            message.setSubject(emailMessage.subject)
            message.setText(emailMessage.message)
            
            mailSender.send(message)
            logger.info("Email sent successfully to: ${emailMessage.email}")
        } catch (e: Exception) {
            logger.error("Failed to send email to: ${emailMessage.email}", e)
            throw RuntimeException("Failed to send email", e)
        }
    }
}
