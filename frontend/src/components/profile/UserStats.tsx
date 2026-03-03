import trophyIcon from "../../assets/profile/trophy.svg";
import bullseyeIcon from "../../assets/profile/bullseye.svg";
import graphUpArrowIcon from "../../assets/profile/graph-up-arrow.svg";
import controllerIcon from "../../assets/profile/controller.svg";

export type UserStatsData = {
  wins?: number;
  losses?: number;
  win_rate?: number;
  total_games?: number;
};

type UserStatsProps = {
  username: string;
  stats: UserStatsData | null;
};

const formatWinRate = (value: number | undefined) => {
  if (value == null) return "0%";

  if (value <= 1) return `${Math.round(value * 100)}%`;

  return `${Math.round(value)}%`;
};

const UserStats = (props: UserStatsProps) => {
  const wins = props.stats?.wins ?? null;
  const losses = props.stats?.losses ?? null;
  const total =
    props.stats?.total_games ??
    (wins !== null && losses !== null ? wins + losses : null);
  const winRate =
    props.stats?.win_rate !== undefined
      ? formatWinRate(props.stats.win_rate)
      : wins !== null && total !== null && total > 0
        ? `${Math.round((wins / total) * 100)}%`
        : total === 0
          ? "0%"
          : null;

  const statItems = [
    {
      icon: trophyIcon,
      alt: "Ícone de vitórias",
      iconClass: "icon-emerald",
      value: wins !== null ? String(wins) : "N/A",
      label: "Vitórias",
    },
    {
      icon: bullseyeIcon,
      alt: "Ícone de derrotas",
      iconClass: "icon-rose",
      value: losses !== null ? String(losses) : "N/A",
      label: "Derrotas",
    },
    {
      icon: graphUpArrowIcon,
      alt: "Ícone de taxa de vitória",
      iconClass: "icon-blue",
      value: winRate ?? "N/A",
      label: "Taxa de Vitória",
    },
    {
      icon: controllerIcon,
      alt: "Ícone de total de jogos",
      iconClass: "icon-cyan",
      value: total !== null ? String(total) : "N/A",
      label: "Total de Jogos",
    },
  ];

  return (
    <dl aria-label={`Estatísticas de ${props.username}`} className="stats-grid">
      {statItems.map((item) => (
        <div key={item.label} className="stat-card">
          <img
            src={item.icon}
            alt={item.alt}
            className={`stat-icon icon-svg ${item.iconClass}`}
          />
          <dd className="stat-value text-white">{item.value}</dd>
          <dt className="stat-label">{item.label}</dt>
        </div>
      ))}
    </dl>
  );
};

export default UserStats;
