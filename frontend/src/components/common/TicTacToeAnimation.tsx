import type { CSSProperties } from "react";

type IconProps = {
  size: number;
  className?: string;
  strokeWidth?: number;
  style?: CSSProperties;
};

const XIcon = ({
  size,
  className = "",
  strokeWidth = 2.5,
  style,
}: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    style={style}
  >
    <path d="M18 6 6 18" />
    <path d="m6 6 12 12" />
  </svg>
);

const CircleIcon = ({
  size,
  className = "",
  strokeWidth = 2.5,
  style,
}: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    style={style}
  >
    <circle cx="12" cy="12" r="9" />
  </svg>
);

const Grid3x3Icon = ({
  size,
  className = "",
  strokeWidth = 2.2,
  style,
}: IconProps) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth={strokeWidth}
    strokeLinecap="round"
    strokeLinejoin="round"
    className={className}
    style={style}
  >
    <rect x="3" y="3" width="18" height="18" rx="2" />
    <path d="M9 3v18M15 3v18M3 9h18M3 15h18" />
  </svg>
);

const floatingItems = [
  { Icon: XIcon, delay: 0.0, duration: 32, size: 22, left: "8%", color: "#3b82f6" },
  { Icon: CircleIcon, delay: 3.4, duration: 32, size: 18, left: "16%", color: "#ef4444" },
  { Icon: Grid3x3Icon, delay: 1.1, duration: 32, size: 20, left: "24%", color: "#22c55e" },
  { Icon: XIcon, delay: 5.7, duration: 32, size: 17, left: "32%", color: "#a855f7" },
  { Icon: CircleIcon, delay: 2.3, duration: 32, size: 24, left: "40%", color: "#f97316" },
  { Icon: Grid3x3Icon, delay: 7.9, duration: 32, size: 18, left: "48%", color: "#06b6d4" },
  { Icon: XIcon, delay: 4.6, duration: 32, size: 20, left: "56%", color: "#ec4899" },
  { Icon: CircleIcon, delay: 9.2, duration: 32, size: 22, left: "64%", color: "#eab308" },
  { Icon: Grid3x3Icon, delay: 6.8, duration: 32, size: 18, left: "72%", color: "#6366f1" },
  { Icon: XIcon, delay: 11.0, duration: 32, size: 20, left: "80%", color: "#14b8a6" },
  { Icon: CircleIcon, delay: 8.1, duration: 32, size: 19, left: "12%", color: "#f43f5e" },
  { Icon: Grid3x3Icon, delay: 12.5, duration: 32, size: 17, left: "28%", color: "#84cc16" },
  { Icon: XIcon, delay: 10.2, duration: 32, size: 21, left: "44%", color: "#0ea5e9" },
  { Icon: CircleIcon, delay: 14.1, duration: 32, size: 18, left: "60%", color: "#fb923c" },
  { Icon: Grid3x3Icon, delay: 13.0, duration: 32, size: 20, left: "76%", color: "#8b5cf6" },
  { Icon: XIcon, delay: 15.6, duration: 32, size: 17, left: "88%", color: "#10b981" },
  { Icon: CircleIcon, delay: 16.7, duration: 32, size: 18, left: "6%", color: "#f59e0b" },
  { Icon: Grid3x3Icon, delay: 18.2, duration: 32, size: 17, left: "20%", color: "#22d3ee" },
  { Icon: XIcon, delay: 17.1, duration: 32, size: 19, left: "34%", color: "#ef4444" },
  { Icon: CircleIcon, delay: 20.4, duration: 32, size: 17, left: "50%", color: "#a3e635" },
  { Icon: Grid3x3Icon, delay: 19.3, duration: 32, size: 19, left: "66%", color: "#3b82f6" },
  { Icon: XIcon, delay: 22.6, duration: 32, size: 18, left: "82%", color: "#f472b6" },
  { Icon: CircleIcon, delay: 21.5, duration: 32, size: 20, left: "92%", color: "#0ea5e9" },
  { Icon: Grid3x3Icon, delay: 24.1, duration: 32, size: 17, left: "14%", color: "#e879f9" },
];

type TicTacToeAnimationProps = {
  phaseShift?: number;
};

const TicTacToeAnimation = ({ phaseShift = 0 }: TicTacToeAnimationProps) => {
  return (
    <div className="relative w-full h-full overflow-hidden">
      <style>{`
        @keyframes floatDiagonal {
          0% {
            transform: translate(0, 120vh) rotate(0deg);
            opacity: 0;
          }
          10% {
            opacity: 1;
          }
          90% {
            opacity: 1;
          }
          100% {
            transform: translate(100px, -120vh) rotate(360deg);
            opacity: 0;
          }
        }
      `}</style>

      {floatingItems.map((item, index) => {
        const { Icon, delay, duration, size, left, color } = item;
        const phaseOffset = (delay + phaseShift) % duration;
        return (
          <div
            key={index}
            className="absolute"
            style={{
              left,
              bottom: "-100px",
              color,
              animationName: "floatDiagonal",
              animationDuration: `${duration}s`,
              animationTimingFunction: "linear",
              animationIterationCount: "infinite",
              animationDelay: `-${phaseOffset}s`,
            }}
          >
            <Icon
              size={size}
              className="opacity-60"
              strokeWidth={2.5}
              style={{
                filter: `drop-shadow(0 0 2px ${color}) drop-shadow(0 0 6px ${color})`,
              }}
            />
          </div>
        );
      })}
    </div>
  );
};

export default TicTacToeAnimation;
