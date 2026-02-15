defmodule EmailsService.EventSubscriber do
  use GenServer
  require Logger

  @channel_welcome "email:welcome"
  @channel_otp "email:otp"

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
        {:redix_pubsub, _pubsub, _ref, :message, %{channel: @channel_welcome, payload: payload}},
        state
      ) do
    Logger.info("Received event on #{@channel_welcome}: #{payload}")
    process_welcome_event(payload)
    {:noreply, state}
  end

  @impl true
  def handle_info(
        {:redix_pubsub, _pubsub, _ref, :message, %{channel: @channel_otp, payload: payload}},
        state
      ) do
    Logger.info("Received event on #{@channel_otp}: #{payload}")
    process_otp_event(payload)
    {:noreply, state}
  end

  @impl true
  def handle_info(msg, state) do
    Logger.debug("EventSubscriber received unknown message: #{inspect(msg)}")
    {:noreply, state}
  end

  defp connect_to_redis(redis_url) do
    with {:ok, pubsub} <- Redix.PubSub.start_link(redis_url),
         {:ok, _ref} <- Redix.PubSub.subscribe(pubsub, @channel_welcome, self()),
         {:ok, _ref} <- Redix.PubSub.subscribe(pubsub, @channel_otp, self()) do
      Logger.info("Subscribed to channels: #{@channel_welcome}, #{@channel_otp}")
      {:ok, pubsub}
    end
  end

  defp process_welcome_event(payload) do
    payload
    |> decode_payload()
    |> send_welcome_email()
  end

  defp process_otp_event(payload) do
    payload
    |> decode_payload()
    |> send_otp_email()
  end

  defp decode_payload(payload) do
    case Jason.decode(payload) do
      {:ok, data} -> {:ok, data}
      {:error, reason} ->
        Logger.error("Failed to decode event payload: #{inspect(reason)}")
        {:error, reason}
    end
  end

  defp send_welcome_email({:ok, %{"email" => email} = _data}) do
    Logger.info("Processing welcome email for: #{email}")

    case EmailsService.Mailer.send_welcome_email(email) do
      {:ok, _} ->
        Logger.info("Welcome email sent successfully to: #{email}")

      {:error, reason} ->
        Logger.error("Failed to send welcome email: #{inspect(reason)}")
    end
  end

  defp send_welcome_email({:error, _reason}), do: :ok

  defp send_otp_email({:ok, %{"email" => email, "otp_code" => otp_code} = _data}) do
    Logger.info("Processing OTP email for: #{email}")

    case EmailsService.Mailer.send_otp_email(email, otp_code) do
      {:ok, _} ->
        Logger.info("OTP email sent successfully to: #{email}")

      {:error, reason} ->
        Logger.error("Failed to send OTP email: #{inspect(reason)}")
    end
  end

  defp send_otp_email({:ok, data}) do
    Logger.error("Invalid OTP event data, missing email or otp_code: #{inspect(data)}")
    :ok
  end

  defp send_otp_email({:error, _reason}), do: :ok
end
