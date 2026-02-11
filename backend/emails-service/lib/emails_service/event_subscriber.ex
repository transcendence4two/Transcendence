defmodule EmailsService.EventSubscriber do
  use GenServer
  require Logger

  @channel "user:registered"

  def start_link(opts) do
    redis_url = Keyword.fetch!(opts, :redis_url)
    GenServer.start_link(__MODULE__, redis_url, name: __MODULE__)
  end

  @impl true
  def init(redis_url) do
    Logger.info("EventSubscriber starting, connecting to Redis...")
    {:ok, pubsub} = Redix.PubSub.start_link(redis_url)
    {:ok, _ref} = Redix.PubSub.subscribe(pubsub, @channel, self())
    Logger.info("Subscribed to channel: #{@channel}")
    {:ok, %{pubsub: pubsub}}
  end

  @impl true
  def handle_info({:redix_pubsub, _pubsub, _ref, :subscribed, %{channel: channel}}, state) do
    Logger.info("Successfully subscribed to: #{channel}")
    {:noreply, state}
  end

  @impl true
  def handle_info({:redix_pubsub, _pubsub, _ref, :message, %{channel: @channel, payload: payload}}, state) do
    Logger.info("Received event on #{@channel}: #{payload}")
    handle_user_registered(payload)
    {:noreply, state}
  end

  @impl true
  def handle_info(msg, state) do
    Logger.debug("EventSubscriber received unknown message: #{inspect(msg)}")
    {:noreply, state}
  end

  defp handle_user_registered(payload) do
    case Jason.decode(payload) do
      {:ok, %{"email" => email, "username" => _username}} ->
        Logger.info("Processing registration email for: #{email}")
        case EmailsService.Mailer.send_email(email) do
          {:ok, _} -> Logger.info("Email sent successfully to: #{email}")
          {:error, reason} -> Logger.error("Failed to send email: #{inspect(reason)}")
        end

      {:error, reason} ->
        Logger.error("Failed to decode event payload: #{inspect(reason)}")
    end
  end
end
