defmodule EmailsService.Swoosh do
  def deliver(email) do
    case Swoosh.Mailer.deliver(email, config()) do
      {:ok, metadata} -> {:ok, metadata}
      {:error, reason} -> {:error, inspect(reason)}
    end
  end

  defp config do
    smtp_config = Application.get_env(:emails_service, :smtp)

    case smtp_config[:username] do
      nil ->
        [adapter: Swoosh.Adapters.Local]

      _ ->
        [
          adapter: Swoosh.Adapters.SMTP,
          relay: smtp_config[:host],
          port: smtp_config[:port],
          username: smtp_config[:username],
          password: smtp_config[:password],
          auth: :always,
          tls: :always
        ]
    end
  end
end
