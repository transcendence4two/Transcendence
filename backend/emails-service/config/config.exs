import Config

config :swoosh,
  :api_client, false

config :logger, :console,
  format: "[$level] $message\n",
  level: :info
