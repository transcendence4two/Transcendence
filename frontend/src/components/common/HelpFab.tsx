import { QuestionLgIcon } from "../icons/Icons";

type ProfileHelpFabProps = {
  ariaLabel?: string;
  onClick?: () => void;
};

const HelpFab = ({ ariaLabel = "Help", onClick }: ProfileHelpFabProps) => {
  return (
    <button
      type="button"
      className="profile-help-fab"
      aria-label={ariaLabel}
      onClick={onClick}
    >
      <QuestionLgIcon className="profile-help-icon icon-white" />
    </button>
  );
};

export default HelpFab;
