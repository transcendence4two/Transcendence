import { BullseyeIcon, TrophyIcon } from "../icons/Icons";

export type MatchHistoryItem = {
  result: "win" | "loss";
  opponent: string | { username?: string; score?: number };
  player?: { score?: number };
  score?: { p1?: number; p2?: number };
};

type MatchHistoryProps = {
  username: string;
  matches: MatchHistoryItem[];
  title?: string;
  className?: string;
};

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
  const history = props.matches;
  const heading = props.title;

  return (
    <section className={`flex flex-col flex-1 min-h-0 ${props.className ?? ""}`}>
      {heading && <h3 className="profile-section-title text-sm">{heading}</h3>}
      {history.length > 0 ? (
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
                  <TrophyIcon className="history-icon icon-svg icon-emerald" />
                ) : (
                  <BullseyeIcon className="history-icon icon-svg icon-rose" />
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
      ) : (
        <div className="flex items-center justify-center p-6 text-slate-500 in-[.light]:text-gray-500">
          <p>No matches played yet.</p>
        </div>
      )}
    </section>
  );
};

export default MatchHistory;
