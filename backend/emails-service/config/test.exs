import Config

config :emails_service, :smtp,
  from_email: "test@transcendence.test"

# Use Swoosh test adapter
config :emails_service, EmailsService.Swoosh,
  adapter: Swoosh.Adapters.Test

config :swoosh, :api_client, false

config :logger, level: :warning
