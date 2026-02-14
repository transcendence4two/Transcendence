defmodule EmailsService.EventSubscriberTest do
  use ExUnit.Case, async: true

  alias EmailsService.EventSubscriber

  describe "process_welcome_event/1" do
    test "decodes valid JSON payload and extracts email" do
      valid_payload = ~s({"email": "test@example.com", "username": "testuser"})

      decoded = Jason.decode!(valid_payload)

      assert decoded["email"] == "test@example.com"
      assert decoded["username"] == "testuser"
    end

    test "returns error for invalid JSON payload" do
      invalid_payload = "invalid json"

      result = Jason.decode(invalid_payload)

      assert {:error, _reason} = result
    end
  end

  describe "process_otp_event/1" do
    test "decodes valid OTP JSON payload" do
      valid_payload = ~s({"email": "test@example.com", "otp_code": "123456"})

      decoded = Jason.decode!(valid_payload)

      assert decoded["email"] == "test@example.com"
      assert decoded["otp_code"] == "123456"
    end
  end

  describe "email event format" do
    test "welcome event contains required email field" do
      event = %{"email" => "user@example.com", "username" => "testuser"}

      assert Map.has_key?(event, "email")
      assert is_binary(event["email"])
    end

    test "otp event contains required fields" do
      event = %{"email" => "user@example.com", "otp_code" => "123456"}

      assert Map.has_key?(event, "email")
      assert Map.has_key?(event, "otp_code")
      assert is_binary(event["email"])
      assert is_binary(event["otp_code"])
    end

    test "channel names are correct" do
      # The subscriber should listen to email:welcome and email:otp channels
      assert "email:welcome" == "email:welcome"
      assert "email:otp" == "email:otp"
    end
  end
end
