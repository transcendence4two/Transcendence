package emails.service.transcendence.domain

data class EmailMessage(
    val email: String,
    val subject: String,
    val message: String
)
