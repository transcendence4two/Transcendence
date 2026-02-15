defmodule EmailsService.Router do
  import Plug.Conn

  def init(opts), do: opts

  def call(conn, _opts) do
    case {conn.method, conn.request_path} do
      {"GET", "/health"} ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(200, Jason.encode!(%{"status" => "ok"}))

      _ ->
        conn
        |> put_resp_content_type("application/json")
        |> send_resp(404, Jason.encode!(%{"error" => "Not found"}))
    end
  end
end
