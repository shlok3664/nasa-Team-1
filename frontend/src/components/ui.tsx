import type { PropsWithChildren, ReactNode } from 'react';

type CardProps = PropsWithChildren<{ title?: string; className?: string; action?: ReactNode }>;

export function Card({ title, className = '', action, children }: CardProps) {
  return (
    <section className={`card ${className}`}>
      {(title || action) && (
        <div className="card-heading">
          {title && <h2>{title}</h2>}
          {action}
        </div>
      )}
      {children}
    </section>
  );
}

export function KpiCard({
  label,
  value,
  detail,
  trend,
  help,
}: {
  label: string;
  value: string;
  detail: string;
  trend?: 'Upward' | 'Downward' | 'Stable';
  help?: string;
}) {
  return (
    <article className="kpi-card">
      <div className="kpi-label">
        <span>{label}</span>
        {help && <InfoTip text={help} />}
      </div>
      <strong className="kpi-value">
        {trend && (
          <span className={`trend-arrow trend-${trend.toLowerCase()}`} aria-hidden="true">
            {trend === 'Upward' ? '↗' : trend === 'Downward' ? '↘' : '→'}
          </span>
        )}
        {value}
      </strong>
      <span className="kpi-detail">{detail}</span>
    </article>
  );
}

export function SegmentedControl<T extends string>({
  label,
  options,
  value,
  onChange,
  className = '',
}: {
  label: string;
  options: readonly T[];
  value: T;
  onChange: (value: T) => void;
  className?: string;
}) {
  return (
    <div className={`segmented-control ${className}`} role="group" aria-label={label}>
      {options.map((option) => (
        <button
          key={option}
          type="button"
          aria-pressed={value === option}
          className={value === option ? 'segment segment-active' : 'segment'}
          onClick={() => onChange(option)}
        >
          {option}
        </button>
      ))}
    </div>
  );
}

export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`skeleton ${className}`} aria-hidden="true" />;
}

export function EmptyState({ title, message }: { title: string; message: string }) {
  return (
    <div className="state-panel" role="status">
      <span className="state-mark" aria-hidden="true">
        —
      </span>
      <h3>{title}</h3>
      <p>{message}</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="state-panel error-state" role="alert">
      <span className="state-mark" aria-hidden="true">
        !
      </span>
      <h3>Analysis unavailable</h3>
      <p>{message}</p>
      <button type="button" className="button button-outline" onClick={onRetry}>
        Retry
      </button>
    </div>
  );
}

export function InfoTip({ text }: { text: string }) {
  return (
    <details className="info-tip">
      <summary aria-label="More information">i</summary>
      <span role="tooltip">{text}</span>
    </details>
  );
}
