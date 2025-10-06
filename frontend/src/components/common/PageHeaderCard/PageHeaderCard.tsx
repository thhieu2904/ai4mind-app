import React from "react";
import "./PageHeaderCard.css";

export interface PageHeaderCardProps {
  // Visual style
  variant?: "primary" | "secondary" | "success" | "warning";
  gradient?: boolean;

  // Header content (Row 1)
  icon?: React.ReactNode;
  title: string;
  subtitle?: string;

  // Description (Row 2)
  description?: string | React.ReactNode;

  // Actions (Row 3)
  actions?: React.ReactNode;

  // Additional styling
  className?: string;
}

export const PageHeaderCard: React.FC<PageHeaderCardProps> = ({
  variant = "primary",
  gradient = true,
  icon,
  title,
  subtitle,
  description,
  actions,
  className = "",
}) => {
  const cardClasses = [
    "page-header-card",
    `page-header-card--${variant}`,
    gradient ? "page-header-card--gradient" : "",
    className,
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <div className={cardClasses}>
      {/* Row 1: Icon + Title | Subtitle */}
      <div className="page-header-card__top">
        <div className="page-header-card__title-section">
          {icon && <div className="page-header-card__icon">{icon}</div>}
          <h1 className="page-header-card__title">{title}</h1>
        </div>

        {subtitle && (
          <div className="page-header-card__subtitle">{subtitle}</div>
        )}
      </div>

      {/* Row 2: Description */}
      {description && (
        <div className="page-header-card__description">{description}</div>
      )}

      {/* Row 3: Action buttons */}
      {actions && <div className="page-header-card__actions">{actions}</div>}
    </div>
  );
};

export default PageHeaderCard;
