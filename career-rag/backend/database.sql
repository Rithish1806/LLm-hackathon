-- ====================================================================
-- EMP-24: AI Career Resource Advisor Database Schema for Supabase
-- Vector database schema using pgvector for semantic retrieval
-- ====================================================================

-- 1. Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create Career Roles Table
CREATE TABLE IF NOT EXISTS career_roles (
    id SERIAL PRIMARY KEY,
    role_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    required_skills TEXT[] NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 3. Create Resources Table with pgvector embedding column (384 dimensions for all-MiniLM-L6-v2)
CREATE TABLE IF NOT EXISTS resources (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    skill VARCHAR(100) NOT NULL,
    role VARCHAR(100) NOT NULL,
    difficulty VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    duration VARCHAR(50) NOT NULL,
    provider VARCHAR(150) NOT NULL,
    url TEXT NOT NULL,
    career_goal VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    verified BOOLEAN DEFAULT true NOT NULL,
    embedding vector(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 4. Create vector index for fast approximate nearest neighbor search
-- Cosine distance operator (<=>)
CREATE INDEX IF NOT EXISTS resources_embedding_cosine_idx 
ON resources USING hnsw (embedding vector_cosine_ops);

-- 5. Stored Procedure (RPC) for Vector Similarity Matching
CREATE OR REPLACE FUNCTION match_resources(
    query_embedding vector(384),
    match_threshold float DEFAULT 0.0,
    match_count int DEFAULT 10,
    filter_role text DEFAULT NULL
)
RETURNS TABLE (
    id int,
    title varchar,
    description text,
    skill varchar,
    role varchar,
    difficulty varchar,
    type varchar,
    duration varchar,
    provider varchar,
    url text,
    career_goal varchar,
    content text,
    verified boolean,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id,
        r.title,
        r.description,
        r.skill,
        r.role,
        r.difficulty,
        r.type,
        r.duration,
        r.provider,
        r.url,
        r.career_goal,
        r.content,
        r.verified,
        1 - (r.embedding <=> query_embedding) AS similarity
    FROM resources r
    WHERE 
        (filter_role IS NULL OR r.role ILIKE '%' || filter_role || '%')
        AND (1 - (r.embedding <=> query_embedding)) >= match_threshold
    ORDER BY r.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- ====================================================================
-- Seed Initial Career Roles
-- ====================================================================
INSERT INTO career_roles (role_name, description, required_skills)
VALUES
(
    'Data Analyst',
    'Analyzes structured and unstructured data to extract business insights, create dashboards, and support decision making.',
    ARRAY['SQL', 'Excel', 'Power BI', 'Statistics', 'Python', 'Data Visualization']
),
(
    'Data Scientist',
    'Applies statistical modeling, machine learning algorithms, and deep data analysis to build predictive systems.',
    ARRAY['Python', 'Statistics', 'Machine Learning', 'SQL', 'Data Visualization']
),
(
    'Software Developer',
    'Designs, develops, tests, and maintains full-stack software applications and services.',
    ARRAY['Python', 'Java', 'C++', 'React', 'Git/GitHub', 'SQL']
),
(
    'Machine Learning Engineer',
    'Builds and deploys scalable machine learning models, neural networks, and inference pipelines.',
    ARRAY['Python', 'Machine Learning', 'Statistics', 'Git/GitHub', 'Cloud']
),
(
    'Business Analyst',
    'Bridges business requirements and technical solutions through data reporting, process modeling, and communication.',
    ARRAY['Excel', 'Power BI', 'Tableau', 'Communication', 'SQL']
),
(
    'Cloud Engineer',
    'Architects, deploys, monitors, and optimizes cloud computing infrastructure and distributed services.',
    ARRAY['Cloud', 'Git/GitHub', 'Python', 'Cybersecurity']
),
(
    'Cybersecurity Analyst',
    'Protects organizational systems, networks, and data from security threats, breaches, and vulnerabilities.',
    ARRAY['Cybersecurity', 'Python', 'Cloud', 'Aptitude']
)
ON CONFLICT (role_name) DO NOTHING;
