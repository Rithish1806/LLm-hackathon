import React from 'react';
import { Calendar, CheckCircle2, ArrowRight } from 'lucide-react';

export default function RoadmapTimeline({ roadmap }) {
  if (!roadmap || roadmap.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <span style={{
          fontSize: '0.75rem',
          fontWeight: '700',
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          color: 'var(--accent-cyan)'
        }}>
          Step 3 • Milestone Pathway
        </span>
        <h2 style={{ fontSize: '1.5rem', marginTop: '0.2rem' }}>Personalized Learning Roadmap</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Structured sequential learning trajectory to transition from your current skills to target role competency.
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '1.5rem',
        position: 'relative'
      }}>
        {roadmap.map((item, index) => (
          <div
            key={index}
            style={{
              backgroundColor: 'rgba(255, 255, 255, 0.02)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '1.5rem',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              position: 'relative'
            }}
          >
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'rgba(99, 102, 241, 0.15)',
                  color: '#a5b4fc',
                  fontSize: '0.75rem',
                  fontWeight: '700'
                }}>
                  <Calendar size={13} />
                  {item.timeline}
                </span>

                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '600' }}>
                  {item.phase}
                </span>
              </div>

              <h4 style={{ fontSize: '1.1rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
                {item.focus_skills.join(' + ')}
              </h4>

              <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: '1.45', marginBottom: '1rem' }}>
                {item.description}
              </p>
            </div>

            <div style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: '0.4rem',
              borderTop: '1px solid var(--border-subtle)',
              paddingTop: '0.75rem'
            }}>
              {item.focus_skills.map((skill, sIdx) => (
                <span key={sIdx} style={{
                  fontSize: '0.75rem',
                  padding: '2px 8px',
                  borderRadius: 'var(--radius-full)',
                  backgroundColor: 'rgba(255, 255, 255, 0.05)',
                  color: 'var(--text-secondary)'
                }}>
                  {skill}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
