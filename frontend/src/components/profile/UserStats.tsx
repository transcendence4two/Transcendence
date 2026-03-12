import {
  BullseyeIcon,
  ControllerFillIcon,
  GraphUpArrowIcon,
  TrophyIcon,
} from "../icons/Icons";

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

const UserStats = (props: UserStatsProps) => {
  const wins = props.stats?.wins ?? null;
  const losses = props.stats?.losses ?? null;
  const total =
    props.stats?.total_games ??
    (wins !== null && losses !== null ? wins + losses : null);
  const winRate =
    total !== null && total > 0
      ? `${Math.round((wins! / total) * 100)}%`
      : total === 0
        ? "0%"
        : null;

  const statItems = [
    {
      icon: <TrophyIcon className="stat-icon icon-svg icon-emerald" />,
      value: wins !== null ? String(wins) : "N/A",
      label: "Wins",
    },
    {
      icon: <BullseyeIcon className="stat-icon icon-svg icon-rose" />,
      value: losses !== null ? String(losses) : "N/A",
      label: "Losses",
    },
    {
      icon: <GraphUpArrowIcon className="stat-icon icon-svg icon-blue" />,
      value: winRate ?? "N/A",
      label: "Win Rate",
    },
    {
      icon: <ControllerFillIcon className="stat-icon icon-svg icon-cyan" />,
      value: total !== null ? String(total) : "N/A",
      label: "Total Games",
    },
  ];

  return (
    <dl aria-label={`${props.username} stats`} className="stats-grid">
      {statItems.map((item) => (
        <div key={item.label} className="stat-card">
          {item.icon}
          <dd className="stat-value text-white">{item.value}</dd>
          <dt className="stat-label">{item.label}</dt>
        </div>
      ))}
    </dl>
  );
};

export default UserStats;
