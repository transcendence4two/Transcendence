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

    case connect_to_redis(redis_url) do
      {:ok, pubsub} ->
        {:ok, %{pubsub: pubsub}}

      {:error, reason} ->
        {:stop, reason}
    end
  end

  @impl true
  def handle_info({:redix_pubsub, _pubsub, _ref, :subscribed, %{channel: channel}}, state) do
    Logger.info("Successfully subscribed to: #{channel}")
    {:noreply, state}
  end

  @impl true
  def handle_info(
        {:redix_pubsub, _pubsub, _ref, :message, %{channel: @channel, payload: payload}},
        state
      ) do
    Logger.info("Received event on #{@channel}: #{payload}")
    process_event(payload)
    {:noreply, state}
  end

  @impl true
  def handle_info(msg, state) do
    Logger.debug("EventSubscriber received unknown message: #{inspect(msg)}")
    {:noreply, state}
  end

  defp connect_to_redis(redis_url) do
    with {:ok, pubsub} <- Redix.PubSub.start_link(redis_url),
         {:ok, _ref} <- Redix.PubSub.subscribe(pubsub, @channel, self()) do
      Logger.info("Subscribed to channel: #{@channel}")
      {:ok, pubsub}
    end
  end

  defp process_event(payload) do
    payload
    |> decode_payload()
    |> send_registration_email()
  end

  defp decode_payload(payload) do
    case Jason.decode(payload) do
      {:ok, data} -> {:ok, data}
      {:error, reason} ->
        Logger.error("Failed to decode event payload: #{inspect(reason)}")
        {:error, reason}
    end
  end

  defp send_registration_email({:ok, %{"email" => email} = _data}) do
    Logger.info("Processing registration email for: #{email}")

    case EmailsService.Mailer.send_email(email) do
      {:ok, _} ->
        Logger.info("Email sent successfully to: #{email}")

      {:error, reason} ->
        Logger.error("Failed to send email: #{inspect(reason)}")
    end
  end

  defp send_registration_email({:error, _reason}), do: :ok
end
