import Config

config :swoosh,
  :api_client, false

config :logger, :console,
  format: "[$level] $message\n",
  level: :info

# Import environment specific config
import_config "#{config_env()}.exs"
