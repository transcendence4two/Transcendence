defmodule EmailsService.LogstashBackend do
  @moduledoc """
  Custom Logger backend that writes ECS-formatted JSON to stdout and
  ships the same payload over TCP to Logstash. Uses only stdlib + Jason.
  Reconnects silently on TCP failure.
  """
  @behaviour :gen_event

  @service_name "emails-service"

  @impl :gen_event
  def init(_args) do
    state = %{
      host: to_charlist(System.get_env("LOGSTASH_HOST", "logstash")),
      port: System.get_env("LOGSTASH_PORT", "5000") |> String.to_integer(),
      service_env: System.get_env("ENV", "development"),
      level: :info,
      socket: nil
    }

    {:ok, connect(state)}
  end

  @impl :gen_event
  def handle_event({level, _group_leader, {Logger, message, timestamp, metadata}}, state) do
    if Logger.compare_levels(level, state.level) != :lt do
      line = build_json_line(level, message, timestamp, metadata, state)
      :io.put_chars(:standard_io, line)
      {:ok, send_to_logstash(state, line)}
    else
      {:ok, state}
    end
  end

  def handle_event(:flush, state), do: {:ok, state}
  def handle_event(_, state), do: {:ok, state}

  @impl :gen_event
  def handle_call({:configure, opts}, state) do
    level = Keyword.get(opts, :level, state.level)
    {:ok, :ok, %{state | level: level}}
  end

  def handle_call(_, state), do: {:ok, :ok, state}

  @impl :gen_event
  def handle_info(_, state), do: {:ok, state}

  @impl :gen_event
  def terminate(_reason, %{socket: socket}) when not is_nil(socket) do
    :gen_tcp.close(socket)
  end

  def terminate(_reason, _state), do: :ok

  @impl :gen_event
  def code_change(_old_vsn, state, _extra), do: {:ok, state}

  # --- Private ---

  defp build_json_line(level, message, timestamp, metadata, state) do
    msg = message |> IO.iodata_to_binary() |> String.trim()

    base = %{
      "@timestamp" => format_timestamp(timestamp),
      "log.level" => format_level(level),
      "message" => msg,
      "service.name" => @service_name,
      "service.environment" => state.service_env
    }

    extra =
      metadata
      |> Keyword.take([:email_type, :action, :channel, :error_type])
      |> Enum.map(fn {k, v} -> {Atom.to_string(k), serialize(v)} end)
      |> Map.new()

    encoded =
      case Jason.encode(Map.merge(base, extra)) do
        {:ok, json} -> json
        {:error, _} -> Jason.encode!(base)
      end

    encoded <> "\n"
  end

  defp format_timestamp({{year, month, day}, {hour, min, sec, ms}}) do
    :io_lib.format(
      "~4..0B-~2..0B-~2..0BT~2..0B:~2..0B:~2..0B.~3..0BZ",
      [year, month, day, hour, min, sec, ms]
    )
    |> IO.iodata_to_binary()
  end

  defp format_level(:debug),   do: "DEBUG"
  defp format_level(:info),    do: "INFO"
  defp format_level(:warn),    do: "WARN"
  defp format_level(:warning), do: "WARN"
  defp format_level(:error),   do: "ERROR"
  defp format_level(other),    do: other |> to_string() |> String.upcase()

  defp serialize(v) when is_binary(v),  do: v
  defp serialize(v) when is_atom(v),    do: Atom.to_string(v)
  defp serialize(v) when is_integer(v), do: v
  defp serialize(v),                    do: inspect(v)

  defp connect(state) do
    case :gen_tcp.connect(state.host, state.port, [:binary, active: false], 5_000) do
      {:ok, socket} -> %{state | socket: socket}
      {:error, _}   -> %{state | socket: nil}
    end
  end

  defp send_to_logstash(%{socket: nil} = state, data) do
    state = connect(state)
    maybe_send(state, data)
  end

  defp send_to_logstash(state, data) do
    case :gen_tcp.send(state.socket, data) do
      :ok -> state
      {:error, _} ->
        :gen_tcp.close(state.socket)
        state = connect(%{state | socket: nil})
        maybe_send(state, data)
    end
  end

  defp maybe_send(%{socket: nil} = state, _data), do: state
  defp maybe_send(state, data) do
    case :gen_tcp.send(state.socket, data) do
      :ok       -> state
      {:error, _} -> %{state | socket: nil}
    end
  end
end
