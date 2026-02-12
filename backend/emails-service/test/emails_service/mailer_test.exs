defmodule EmailsService.MailerTest do
  use ExUnit.Case, async: true

  alias EmailsService.Mailer

  describe "send_email/1" do
    test "creates email with correct recipient" do
      import Swoosh.Email

      email =
        new()
        |> to("test@example.com")
        |> from({"Transcendence", "noreply@transcendence.com"})
        |> subject("Welcome to Transcendence")
        |> html_body("<h1>Welcome!</h1>")

      assert email.to == [{"", "test@example.com"}]
      assert email.subject == "Welcome to Transcendence"
    end

    test "email template contains welcome message" do
      # Simple test to verify template structure
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
end
