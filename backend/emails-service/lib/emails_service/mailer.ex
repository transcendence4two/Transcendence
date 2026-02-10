defmodule EmailsService.Mailer do
  import Swoosh.Email

  def send_email(recipient_email) do
    new()
    |> to(recipient_email)
    |> from(from_email())
    |> subject("Welcome to Transcendence")
    |> html_body(join_email_template(recipient_email))
    |> EmailsService.Swoosh.deliver()
  end

  defp from_email do
    config = Application.get_env(:emails_service, :smtp)
    config[:from_email]
  end

  defp join_email_template(email) do
    """
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h1>Welcome to Transcendence!</h1>
        <p>Hello #{email},</p>
        <p>Thank you for joining our platform. We're excited to have you on board!</p>
        <p>Best regards,<br>Transcendence Team</p>
      </body>
    </html>
    """
  end
end
