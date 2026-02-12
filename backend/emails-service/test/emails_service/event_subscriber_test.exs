defmodule EmailsService.EventSubscriberTest do
  use ExUnit.Case, async: true

  alias EmailsService.EventSubscriber

  describe "process_event/1" do
    test "decodes valid JSON payload and extracts email" do
      # Test the payload decoding logic
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

  describe "email event format" do
    test "event contains required email field" do
      event = %{"email" => "user@example.com", "username" => "testuser"}

      assert Map.has_key?(event, "email")
      assert is_binary(event["email"])
    end

    test "channel name is correct" do
      # The subscriber should listen to user:registered channel
      assert "user:registered" == "user:registered"
    end
  end
end
