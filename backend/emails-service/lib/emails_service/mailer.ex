defmodule EmailsService.Mailer do
  import Swoosh.Email

  def send_welcome_email(recipient_email) do
    new()
    |> to(recipient_email)
    |> from(from_email())
    |> subject("Welcome to Transcendence")
    |> html_body(welcome_email_template(recipient_email))
    |> EmailsService.Swoosh.deliver()
  end

  def send_otp_email(recipient_email, otp_code) do
    new()
    |> to(recipient_email)
    |> from(from_email())
    |> subject("Your Transcendence Verification Code")
    |> html_body(otp_email_template(otp_code))
    |> EmailsService.Swoosh.deliver()
  end

  defp from_email do
    config = Application.get_env(:emails_service, :smtp)
    config[:from_email]
  end

  defp welcome_email_template(email) do
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

  defp otp_email_template(otp_code) do
    """
    <html>
      <body style="font-family: Arial, sans-serif; padding: 20px;">
        <h1>Your Verification Code</h1>
        <p>Use the following code to complete your two-factor authentication:</p>
        <div style="background-color: #f4f4f4; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0;">
          <span style="font-size: 32px; font-weight: bold; letter-spacing: 5px; color: #333;">#{otp_code}</span>
        </div>
        <p>This code will expire in 5 minutes.</p>
        <p>If you didn't request this code, please ignore this email.</p>
        <p>Best regards,<br>Transcendence Team</p>
      </body>
    </html>
    """
  end
end
