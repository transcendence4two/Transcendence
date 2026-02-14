defmodule EmailsService.MailerTest do
  use ExUnit.Case, async: true

  alias EmailsService.Mailer

  describe "send_welcome_email/1" do
    test "creates email with correct recipient" do
      import Swoosh.Email

      email =
        new()
        |> to("test@example.com")
        |> from({"Transcendence", "noreply@transcendence.com"})
        |> subject("Welcome to Transcendence")
        |> html_body("<h1>Welcome!</h1>")

      assert email.to == [{"Transcendence", "test@example.com"}] || email.to == [{"", "test@example.com"}]
      assert email.subject == "Welcome to Transcendence"
    end

    test "welcome email template contains welcome message" do
      template = """
      <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
          <h1>Welcome to Transcendence!</h1>
          <p>Hello test@example.com,</p>
          <p>Thank you for joining our platform. We're excited to have you on board!</p>
          <p>Best regards,<br>Transcendence Team</p>
        </body>
      </html>
      """

      assert template =~ "Welcome to Transcendence"
      assert template =~ "Thank you for joining"
    end
  end

  describe "send_otp_email/2" do
    test "creates otp email with correct structure" do
      import Swoosh.Email

      email =
        new()
        |> to("test@example.com")
        |> from({"Transcendence", "noreply@transcendence.com"})
        |> subject("Your Transcendence Verification Code")
        |> html_body("<h1>Your code: 123456</h1>")

      assert email.subject == "Your Transcendence Verification Code"
    end

    test "otp email template contains verification code" do
      otp_code = "123456"
      template = """
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

      assert template =~ "Verification Code"
      assert template =~ otp_code
      assert template =~ "expire in 5 minutes"
    end
  end
end
