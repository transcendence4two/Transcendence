defmodule EmailsService.Router do
  import Plug.Conn
  require Logger

  def init(opts) do
    opts
  end

  def call(conn, _opts) do
    Logger.info("Request: #{conn.method} #{conn.request_path}")
    case {conn.method, String.split(conn.request_path, "/")} do
      {"POST", ["", "emails", "send"]} ->
        send_email(conn)

      _ ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(404, Jason.encode!(%{"error" => "Not found"}))
    end
  end

  defp send_email(conn) do
    {:ok, body, conn} = Plug.Conn.read_body(conn)
    Logger.info("Received body: #{body}")

    case Jason.decode(body) do
      {:ok, %{"email" => email}} when is_binary(email) ->
        Logger.info("Sending email to: #{email}")
        case EmailsService.Mailer.send_email(email) do
          {:ok, _} ->
            Logger.info("Email sent successfully")
            conn
            |> put_resp_content_type("application/json")
            |> send_resp(200, Jason.encode!(%{"status" => "email sent"}))

          {:error, reason} ->
            Logger.error("Failed to send email: #{inspect(reason)}")
            conn
            |> put_resp_content_type("application/json")
            |> send_resp(500, Jason.encode!(%{"error" => reason}))
        end

      {:ok, _} ->
        Logger.warn("Missing email field in request")
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(400, Jason.encode!(%{"error" => "email field is required"}))

      {:error, _} ->
        Logger.warn("Invalid JSON in request")
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(400, Jason.encode!(%{"error" => "invalid json"}))
    end
  end
end
