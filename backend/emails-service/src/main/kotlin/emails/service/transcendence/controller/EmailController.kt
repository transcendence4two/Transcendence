package emails.service.transcendence.controller

import emails.service.transcendence.application.EmailService
import emails.service.transcendence.domain.EmailMessage
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.*
import org.slf4j.LoggerFactory

@RestController
@RequestMapping("/api/emails")
class EmailController(
    private val emailService: EmailService
) {
    private val logger = LoggerFactory.getLogger(EmailController::class.java)

    @PostMapping("/send")
    fun sendEmail(@RequestBody emailMessage: EmailMessage): ResponseEntity<Map<String, String>> {
        return try {
            emailService.sendEmail(emailMessage)
            ResponseEntity.ok(mapOf("status" to "Email sent successfully to ${emailMessage.email}"))
        } catch (e: Exception) {
            logger.error("Error sending email", e)
            ResponseEntity.status(500).body(mapOf("error" to e.message.orEmpty()))
        }
    }

    @GetMapping("/health")
    fun health(): ResponseEntity<Map<String, String>> {
        return ResponseEntity.ok(mapOf("status" to "Email service is running"))
    }
}
