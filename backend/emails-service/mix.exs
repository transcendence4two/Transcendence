defmodule EmailsService.MixProject do
  use Mix.Project

  def project do
    [
      app: :emails_service,
      version: "0.1.0",
      elixir: "~> 1.14",
      start_permanent: Mix.env() == :prod,
      deps: deps()
    ]
  end

  def application do
    [
      extra_applications: [:logger],
      mod: {EmailsService.Application, []}
    ]
  end

  defp deps do
    [
      {:plug_cowboy, "~> 2.6"},
      {:plug, "~> 1.14"},
      {:jason, "~> 1.4"},
      {:swoosh, "~> 1.8"},
      {:gen_smtp, "~> 1.2"},
      {:dotenv, "~> 3.0"}
    ]
  end
end
