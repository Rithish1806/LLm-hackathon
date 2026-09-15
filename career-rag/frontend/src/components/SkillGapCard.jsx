import React from 'react';
import { Target, CheckCircle2, AlertCircle, Clock, Award } from 'lucide-react';

export default function SkillGapCard({ data }) {
  if (!data) return null;

  const { target_role, current_level, career_goal, available_time, skill_gap } = data;
  const coverage = skill_gap?.coverage_percent ?? 0;

  return (
    <div className="glass-panel" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '1.25rem',
        marginBottom: '1.5rem'
      }}>
        <div>
          <span style={{
            fontSize: '0.75rem',
            fontWeight: '700',
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: 'var(--accent-cyan)'
          }}>
            Step 1 • Profile & Gap Analysis
          </span>
          <h2 style={{ fontSize: '1.5rem', marginTop: '0.2rem' }}>
            Career Readiness: <span style={{ color: 'var(--accent-primary)' }}>{target_role}</span>
          </h2>
        </div>

        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <Award size={16} color="var(--accent-amber)" />
            <span><strong>Level:</strong> {current_level}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <Target size={16} color="var(--accent-cyan)" />
            <span><strong>Goal:</strong> {career_goal}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <Clock size={16} color="var(--accent-emerald)" />
            <span><strong>Time:</strong> {available_time}</span>
          </div>
        </div>
      </div>

      {/* Coverage Progress Bar */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem', fontSize: '0.875rem' }}>
          <span style={{ fontWeight: '600' }}>Role Skill Match</span>
          <span style={{ fontWeight: '700', color: coverage >= 70 ? 'var(--accent-emerald)' : 'var(--accent-amber)' }}>
            {coverage}% Matched
          </span>
        </div>
        <div style={{
          height: '10px',
          backgroundColor: 'rgba(255, 255, 255, 0.06)',
          borderRadius: '999px',
          overflow: 'hidden',
          border: '1px solid var(--border-subtle)'
        }}>
          <div style={{
            height: '100%',
            width: `${coverage}%`,
            background: coverage >= 70 ? 'var(--accent-emerald)' : 'linear-gradient(90deg, #f59e0b, #6366f1)',
            borderRadius: '999px',
            transition: 'width 0.6s ease'
          }} />
        </div>
      </div>

      {/* Existing vs Missing Skills Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {/* Acquired Skills */}
        <div style={{
          backgroundColor: 'rgba(16, 185, 129, 0.05)',
          border: '1px solid rgba(16, 185, 129, 0.2)',
          borderRadius: 'var(--radius-md)',
          padding: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.75rem' }}>
            <CheckCircle2 size={18} color="var(--accent-emerald)" />
            <h3 style={{ fontSize: '1rem', color: '#34d399' }}>
              Acquired Skills ({skill_gap?.known_skills?.length || 0})
            </h3>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {skill_gap?.known_skills && skill_gap.known_skills.length > 0 ? (
              skill_gap.known_skills.map(skill => (
                <span key={skill} style={{
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.8rem',
                  fontWeight: '600',
                  backgroundColor: 'rgba(16, 185, 129, 0.15)',
                  color: '#6ee7b7',
                  border: '1px solid rgba(16, 185, 129, 0.3)'
                }}>
                  ✓ {skill}
                </span>
              ))
            ) : (
              <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>No matching required skills found.</span>
            )}
          </div>
        </div>

        {/* Missing Skills */}
        <div style={{
          backgroundColor: 'rgba(244, 63, 94, 0.05)',
          border: '1px solid rgba(244, 63, 94, 0.2)',
          borderRadius: 'var(--radius-md)',
          padding: '1.25rem'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '0.75rem' }}>
            <AlertCircle size={18} color="var(--accent-rose)" />
            <h3 style={{ fontSize: '1rem', color: '#fb7185' }}>
              Skill Gaps to Target ({skill_gap?.missing_skills?.length || 0})
            </h3>
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
            {skill_gap?.missing_skills && skill_gap.missing_skills.length > 0 ? (
              skill_gap.missing_skills.map(skill => (
                <span key={skill} style={{
                  padding: '4px 10px',
                  borderRadius: 'var(--radius-full)',
                  fontSize: '0.8rem',
                  fontWeight: '600',
                  backgroundColor: 'rgba(244, 63, 94, 0.15)',
                  color: '#fda4af',
                  border: '1px solid rgba(244, 63, 94, 0.3)'
                }}>
                  ❌ {skill}
                </span>
              ))
            ) : (
              <span style={{ fontSize: '0.85rem', color: 'var(--accent-emerald)' }}>All core skills matched! Focusing on specialization.</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
