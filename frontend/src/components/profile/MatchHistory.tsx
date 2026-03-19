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
    <section
      className={`flex flex-col flex-1 min-h-0 text-left space-y-3 ${props.className ?? ""}`}
    >
      {heading && history.length > 0 && (
        <h3 className="profile-section-title mt-4 mb-2 text-sm">{heading}</h3>
      )}
      {heading && history.length === 0 && (
        <hr className="history-empty-divider" aria-hidden="true" />
      )}
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
        <div className="history-empty-state" role="status" aria-live="polite">
          <div className="history-empty-icon-ring" aria-hidden="true">
            <span className="history-empty-ring-pulse" />
            <span className="history-empty-ring-pulse history-empty-ring-pulse-2" />
            <svg
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="history-empty-icon"
            >
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
          </div>
          <div className="history-empty-text-wrap">
            <p className="history-empty-title">No matches played yet</p>
            <p className="history-empty-subtitle">
              Play your first match to start building your history
            </p>
          </div>
        </div>
      )}
    </section>
  );
};

export default MatchHistory;
