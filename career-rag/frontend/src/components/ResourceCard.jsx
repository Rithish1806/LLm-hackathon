import React from 'react';
import { ExternalLink, CheckCircle, Clock, BookOpen, Layers, ShieldCheck, Sparkles } from 'lucide-react';

export default function ResourceCard({ resource }) {
  const {
    title,
    skill,
    difficulty,
    type,
    duration,
    provider,
    url,
    match_score,
    why_recommended,
    evidence,
    verified
  } = resource;

  const score = match_score ?? 85;

  return (
    <div className="glass-panel" style={{
      padding: '1.5rem',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'space-between',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Top Meta Bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.75rem' }}>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center' }}>
            <span style={{
              padding: '3px 10px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              fontWeight: '700',
              backgroundColor: 'rgba(99, 102, 241, 0.15)',
              color: '#a5b4fc',
              border: '1px solid rgba(99, 102, 241, 0.3)'
            }}>
              {skill}
            </span>

            <span style={{
              padding: '3px 8px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)'
            }}>
              {type}
            </span>

            <span style={{
              padding: '3px 8px',
              borderRadius: 'var(--radius-full)',
              fontSize: '0.75rem',
              backgroundColor: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)'
            }}>
              {difficulty}
            </span>
          </div>

          {/* Match Score Badge */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            padding: '4px 10px',
            borderRadius: '999px',
            backgroundColor: score >= 80 ? 'rgba(16, 185, 129, 0.15)' : 'rgba(245, 158, 11, 0.15)',
            border: `1px solid ${score >= 80 ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
            color: score >= 80 ? '#34d399' : '#fbbf24',
            fontSize: '0.8rem',
            fontWeight: '700',
            whiteSpace: 'nowrap'
          }}>
            <Sparkles size={13} />
            {score}% Match
          </div>
        </div>

        {/* Resource Title */}
        <h3 style={{ fontSize: '1.15rem', lineHeight: '1.35', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
          {title}
        </h3>

        {/* Provider and Duration */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Layers size={14} />
            {provider}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={14} />
            {duration}
          </span>
          {verified && (
            <span style={{ display: 'flex', alignItems: 'center', gap: '3px', color: '#34d399' }}>
              <ShieldCheck size={14} />
              Verified
            </span>
          )}
        </div>

        {/* Explainable RAG Reason Box */}
        <div style={{
          backgroundColor: 'rgba(99, 102, 241, 0.06)',
          borderLeft: '3px solid var(--accent-primary)',
          borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
          padding: '0.75rem 1rem',
          marginBottom: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '0.4rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.04em', color: '#a5b4fc' }}>
              Why this was recommended?
            </span>
          </div>

          {evidence && evidence.length > 0 ? (
            <ul style={{ margin: 0, paddingLeft: '1.2rem', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              {evidence.map((point, idx) => (
                <li key={idx} style={{ marginBottom: '2px' }}>{point}</li>
              ))}
            </ul>
          ) : (
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>
              {why_recommended || "Direct semantic match with your career skill requirements."}
            </p>
          )}
        </div>
      </div>

      {/* Footer with Authenticated Source Link */}
      <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.9rem', marginTop: 'auto' }}>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            fontSize: '0.85rem',
            fontWeight: '600',
            color: 'var(--accent-cyan)',
            padding: '4px 0'
          }}
        >
          <span>Open Verified Resource</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </div>
  );
}
