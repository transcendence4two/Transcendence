defmodule EmailsService.Application do
  use Application
  require Logger

  @impl true
  def start(_type, _args) do
    redis_url = System.get_env("REDIS_URL", "redis://localhost:6379")
    Logger.info("Connecting to Redis at: #{redis_url}")

    children = [
      {Plug.Cowboy, scheme: :http, plug: EmailsService.Router, options: [port: 4001]},
      {EmailsService.EventSubscriber, redis_url: redis_url}
    ]

    opts = [strategy: :one_for_one, name: EmailsService.Supervisor]
    Supervisor.start_link(children, opts)
  end
end
