import trophyIcon from "../../assets/profile/trophy.svg";
import bullseyeIcon from "../../assets/profile/bullseye.svg";

export type MatchHistoryItem = {
  result: "win" | "loss";
  opponent: string | { username?: string; score?: number };
  player?: { score?: number };
  score?: { p1?: number; p2?: number };
};

type MatchHistoryProps = {
  username: string;
  matches: MatchHistoryItem[];
};

const fallbackMatches: MatchHistoryItem[] = [
  {
    result: "win",
    opponent: { username: "noob", score: 8 },
    player: { score: 11 },
  },
  {
    result: "win",
    opponent: { username: "noob", score: 6 },
    player: { score: 11 },
  },
  {
    result: "loss",
    opponent: { username: "noob", score: 11 },
    player: { score: 10 },
  },
];

const getOpponentName = (opponent: MatchHistoryItem["opponent"]) => {
  if (typeof opponent === "string") return opponent;
  return opponent.username ?? "oponente";
};

const getMatchScore = (match: MatchHistoryItem) => {
  const playerScore = match.player?.score ?? match.score?.p1 ?? 0;
  const opponentScore =
    (typeof match.opponent === "string" ? undefined : match.opponent.score) ??
    match.score?.p2 ??
    0;

  return `${playerScore} - ${opponentScore}`;
};

const MatchHistory = (props: MatchHistoryProps) => {
  const history = props.matches.length > 0 ? props.matches : fallbackMatches;

  return (
    <dl
      aria-label={`Histórico de partidas de ${props.username}`}
      className="history-list"
    >
      {history.map((match, index) => (
        <div key={index} className="history-item">
          <span
            className={`history-icon-badge ${match.result === "win" ? "history-icon-badge-win" : "history-icon-badge-loss"}`}
          >
            <img
              src={match.result === "win" ? trophyIcon : bullseyeIcon}
              alt={
                match.result === "win" ? "Ícone de vitória" : "Ícone de derrota"
              }
              className={`history-icon icon-svg ${match.result === "win" ? "icon-emerald" : "icon-rose"}`}
            />
          </span>
          <dt className="history-text">
            {match.result === "win" ? "Vitória" : "Derrota"} vs{" "}
            {getOpponentName(match.opponent)}
          </dt>
          <dd
            className={`history-score ${match.result === "win" ? "history-score-win" : "history-score-loss"}`}
          >
            {getMatchScore(match)}
          </dd>
        </div>
      ))}
    </dl>
  );
};

export default MatchHistory;
