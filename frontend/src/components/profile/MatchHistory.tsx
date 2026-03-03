import { BullseyeFillIcon, TrophyFillIcon } from "../icons/Icons";

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
    opponent: { username: "noob", score: 1 },
    player: { score: 3 },
  },
  {
    result: "win",
    opponent: { username: "noob", score: 0 },
    player: { score: 3 },
  },
  {
    result: "loss",
    opponent: { username: "noob", score: 3 },
    player: { score: 2 },
  },
];

const getOpponentName = (opponent: MatchHistoryItem["opponent"]) => {
  if (typeof opponent === "string") return opponent;
  return opponent.username ?? "opponent";
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
      aria-label={`${props.username} match history`}
      className="history-list"
    >
      {history.map((match, index) => (
        <div key={index} className="history-item">
          <span
            className={`history-icon-badge ${match.result === "win" ? "history-icon-badge-win" : "history-icon-badge-loss"}`}
          >
            {match.result === "win" ? (
              <TrophyFillIcon className="history-icon icon-svg icon-emerald" />
            ) : (
              <BullseyeFillIcon className="history-icon icon-svg icon-rose" />
            )}
          </span>
          <dt className="history-text">
            {match.result === "win" ? "Win" : "Loss"} vs{" "}
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
