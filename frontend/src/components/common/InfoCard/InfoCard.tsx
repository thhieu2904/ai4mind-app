import React from "react";
import "./InfoCard.css";

export interface InfoCardProps {
  // Core visual style
  variant?: "primary" | "secondary" | "success" | "warning" | "plain";
  gradient?: boolean;

  // Header content
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  headerExtra?: React.ReactNode;

  // Main content
  children: React.ReactNode;

  // Actions slot
  actions?: React.ReactNode;

  // Behavior
  clickable?: boolean;
  onClick?: () => void;

  // Additional styling
  className?: string;
}

export const InfoCard: React.FC<InfoCardProps> = ({
  variant = "plain",
  gradient = false,
  title,
  subtitle,
  icon,
  headerExtra,
  children,
  actions,
  clickable = false,
  onClick,
  className = "",
}) => {
  const cardClasses = [
    "info-card",
    `info-card--${variant}`,
    gradient ? "info-card--gradient" : "",
    clickable ? "info-card--clickable" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div
      className={cardClasses}
      onClick={clickable ? onClick : undefined}
      role={clickable ? "button" : undefined}
      tabIndex={clickable ? 0 : undefined}
    >
      {/* Header section */}
      {(icon || title || subtitle || headerExtra) && (
        <div className="info-card__header">
          {icon && <div className="info-card__icon">{icon}</div>}

          <div className="info-card__header-content">
            {title && <h3 className="info-card__title">{title}</h3>}
            {subtitle && <p className="info-card__subtitle">{subtitle}</p>}
          </div>

          {headerExtra && (
            <div className="info-card__header-extra">{headerExtra}</div>
          )}
        </div>
      )}

      {/* Body section */}
      <div className="info-card__body">{children}</div>

      {/* Actions section */}
      {actions && <div className="info-card__actions">{actions}</div>}
    </div>
  );
};

export default InfoCard;
