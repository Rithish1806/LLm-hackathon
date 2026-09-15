import React, { useState } from 'react';
import { Sparkles, FileText, Check, Plus, X } from 'lucide-react';

const COMMON_SKILLS = [
  "SQL", "Excel", "Python", "Power BI", "Tableau", "Statistics",
  "Machine Learning", "Data Visualization", "Java", "C++", "React",
  "Git/GitHub", "Cloud", "Cybersecurity", "Communication", "Aptitude"
];

const ROLES = [
  "Data Analyst",
  "Data Scientist",
  "Software Developer",
  "Machine Learning Engineer",
  "Business Analyst",
  "Cloud Engineer",
  "Cybersecurity Analyst"
];

export default function CareerForm({ onSubmit, loading }) {
  const [targetRole, setTargetRole] = useState("Data Analyst");
  const [currentLevel, setCurrentLevel] = useState("Beginner");
  const [selectedSkills, setSelectedSkills] = useState(["Excel", "Python"]);
  const [customSkill, setCustomSkill] = useState("");
  const [careerGoal, setCareerGoal] = useState("Placement");
  const [availableTime, setAvailableTime] = useState("3 months");
  const [hoursPerWeek, setHoursPerWeek] = useState(10);
  const [jobDescription, setJobDescription] = useState("");
  const [showJdInput, setShowJdInput] = useState(false);

  const toggleSkill = (skill) => {
    if (selectedSkills.includes(skill)) {
      setSelectedSkills(selectedSkills.filter(s => s !== skill));
    } else {
      setSelectedSkills([...selectedSkills, skill]);
    }
  };

  const addCustomSkill = (e) => {
    e.preventDefault();
    if (customSkill.trim() && !selectedSkills.includes(customSkill.trim())) {
      setSelectedSkills([...selectedSkills, customSkill.trim()]);
      setCustomSkill("");
    }
  };

  const removeSkill = (skillToRemove) => {
    setSelectedSkills(selectedSkills.filter(s => s !== skillToRemove));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      target_role: targetRole,
      current_level: currentLevel,
      current_skills: selectedSkills,
      career_goal: careerGoal,
      available_time: availableTime,
      hours_per_week: Number(hoursPerWeek),
      job_description: jobDescription.trim() ? jobDescription.trim() : null
    });
  };

  return (
    <div className="glass-panel" style={{ padding: '2rem' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Personalize Your Career Guidance</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
          Provide your target career aspirations. Our RAG engine will identify your skill gaps and retrieve verified, explainable learning pathways.
        </p>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {/* Row 1: Target Role and Current Level */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              Target Career / Role *
            </label>
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            >
              {ROLES.map(role => (
                <option key={role} value={role} style={{ backgroundColor: '#0f172a' }}>{role}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              Current Skill Level *
            </label>
            <select
              value={currentLevel}
              onChange={(e) => setCurrentLevel(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem',
                outline: 'none'
              }}
            >
              <option value="Beginner" style={{ backgroundColor: '#0f172a' }}>Beginner (0-1 yrs)</option>
              <option value="Intermediate" style={{ backgroundColor: '#0f172a' }}>Intermediate (1-3 yrs)</option>
              <option value="Advanced" style={{ backgroundColor: '#0f172a' }}>Advanced (3+ yrs)</option>
            </select>
          </div>
        </div>

        {/* Current Skills Selection */}
        <div>
          <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
            Your Current Skills (Click to select)
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '0.75rem' }}>
            {COMMON_SKILLS.map(skill => {
              const isSelected = selectedSkills.includes(skill);
              return (
                <button
                  type="button"
                  key={skill}
                  onClick={() => toggleSkill(skill)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                    padding: '6px 12px',
                    borderRadius: 'var(--radius-full)',
                    fontSize: '0.8rem',
                    fontWeight: '600',
                    cursor: 'pointer',
                    border: isSelected ? '1px solid var(--accent-primary)' : '1px solid var(--border-subtle)',
                    backgroundColor: isSelected ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.03)',
                    color: isSelected ? '#a5b4fc' : 'var(--text-secondary)',
                    transition: 'all 0.15s ease'
                  }}
                >
                  {isSelected && <Check size={14} />}
                  {skill}
                </button>
              );
            })}
          </div>

          {/* Add Custom Skill input */}
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input
              type="text"
              placeholder="Add other skill (e.g. Docker, NLP)..."
              value={customSkill}
              onChange={(e) => setCustomSkill(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') addCustomSkill(e); }}
              style={{
                flex: 1,
                padding: '0.6rem 0.9rem',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.85rem'
              }}
            />
            <button
              type="button"
              onClick={addCustomSkill}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '0.6rem 1rem',
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                fontSize: '0.85rem'
              }}
            >
              <Plus size={16} />
              Add
            </button>
          </div>
        </div>

        {/* Row 2: Career Goal, Available Time, Hours/Week */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              Career Goal *
            </label>
            <select
              value={careerGoal}
              onChange={(e) => setCareerGoal(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem'
              }}
            >
              <option value="Placement" style={{ backgroundColor: '#0f172a' }}>Campus Placement</option>
              <option value="Job" style={{ backgroundColor: '#0f172a' }}>Full-Time Job</option>
              <option value="Internship" style={{ backgroundColor: '#0f172a' }}>Internship</option>
              <option value="Certification" style={{ backgroundColor: '#0f172a' }}>Industry Certification</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              Available Time *
            </label>
            <select
              value={availableTime}
              onChange={(e) => setAvailableTime(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem'
              }}
            >
              <option value="1 month" style={{ backgroundColor: '#0f172a' }}>1 Month (Fast-track)</option>
              <option value="3 months" style={{ backgroundColor: '#0f172a' }}>3 Months (Standard)</option>
              <option value="6 months" style={{ backgroundColor: '#0f172a' }}>6 Months (Comprehensive)</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '600', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>
              Hours / Week *
            </label>
            <input
              type="number"
              min="2"
              max="60"
              value={hoursPerWeek}
              onChange={(e) => setHoursPerWeek(e.target.value)}
              style={{
                width: '100%',
                padding: '0.75rem 1rem',
                backgroundColor: 'var(--bg-input)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                color: 'var(--text-primary)',
                fontSize: '0.95rem'
              }}
            />
          </div>
        </div>

        {/* Optional Job Description Toggle */}
        <div style={{ marginTop: '0.5rem' }}>
          <button
            type="button"
            onClick={() => setShowJdInput(!showJdInput)}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--accent-cyan)',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.875rem',
              fontWeight: '600',
              padding: 0
            }}
          >
            <FileText size={16} />
            {showJdInput ? "Hide Job Description Input" : "+ Paste a Job Description for Targeted Skill Extraction"}
          </button>

          {showJdInput && (
            <div style={{ marginTop: '0.75rem' }}>
              <textarea
                placeholder="Paste job posting description here... The RAG engine will extract required technical skills and compare them directly against your current skill set."
                rows={4}
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem 1rem',
                  backgroundColor: 'var(--bg-input)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-md)',
                  color: 'var(--text-primary)',
                  fontSize: '0.85rem',
                  lineHeight: '1.4',
                  resize: 'vertical'
                }}
              />
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          style={{
            marginTop: '0.5rem',
            padding: '1rem 2rem',
            background: 'var(--gradient-brand)',
            color: '#ffffff',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            fontWeight: '700',
            fontSize: '1rem',
            cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.7 : 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)',
            transition: 'transform 0.15s ease'
          }}
        >
          {loading ? (
            <>
              <div style={{
                width: '18px',
                height: '18px',
                border: '2px solid #ffffff',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite'
              }} />
              <span>Analyzing Skill Gaps & Retrieving Resources...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Generate Career Plan</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
