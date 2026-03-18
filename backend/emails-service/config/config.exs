import Config

config :swoosh,
  :api_client, false

config :logger,
  backends: [EmailsService.LogstashBackend],
  level: :info

# Import environment specific config
import_config "#{config_env()}.exs"
