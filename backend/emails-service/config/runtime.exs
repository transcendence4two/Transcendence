import Config

if File.exists?(".env"), do: Dotenv.load!()

config :emails_service, :smtp,
  host: System.get_env("SMTP_HOST", "localhost"),
  port: String.to_integer(System.get_env("SMTP_PORT", "1025")),
  username: System.get_env("SMTP_USER"),
  password: System.get_env("SMTP_PASSWORD"),
  from_email: System.get_env("SMTP_FROM_EMAIL", "noreply@transcendence.local")
