# EMP-24: AI Career Resource Advisor using RAG (Retrieval-Augmented Generation)

An explainable, grounded AI-powered Career Resource Recommendation System built for the **EMP-24 Competition**. It performs role-based and job-description skill gap analysis, semantic vector retrieval over a curated knowledge base, multi-factor re-ranking, and grounded learning path generation with source citations.

---

## 1. Problem Statement
Students and early-career job seekers struggle to find trustworthy, relevant, and level-appropriate learning resources. Generic search engines produce thousands of uncurated results, while conventional generative AI chatbots frequently hallucinate non-existent courses, dead links, inaccurate durations, or outdated prerequisites.

## 2. Solution
The **AI Career Resource Advisor** solves this using **Retrieval-Augmented Generation (RAG)**:
- Compares user proficiencies against industry role requirements or uploaded job descriptions to identify exact skill gaps.
- Semantically retrieves verified learning resources from a curated knowledge base using pgvector embeddings.
- Ranks candidate resources using a multi-factor scoring formula (semantic similarity, role relevance, skill-gap coverage, difficulty, career goal).
- Generates a structured month-by-month learning roadmap and explainable "Why this was recommended" evidence cards.
- Never invents courses or URLs; every recommendation directly links to a verified public source.

---

## 3. What is RAG (Retrieval-Augmented Generation)?
Retrieval-Augmented Generation is an AI architectural pattern that grounds Large Language Models on verified external information rather than relying purely on model internal memory:
1. **Retrieve**: Given a user query, find the most semantically relevant documents from a vetted database.
2. **Augment**: Inject the retrieved factual context directly into the LLM prompt with strict boundary instructions.
3. **Generate**: The LLM synthesizes a coherent, personalized, and grounded response strictly supported by the retrieved facts, citing authentic sources.

---

## 4. System Architecture

```
                                  +---------------------------------------+
                                  |         Student / Learner UI          |
                                  | React + Vite + Modern Glass Dashboard |
                                  +-------------------+-------------------+
                                                      |
                                                      | HTTP / JSON REST
                                                      v
                                  +---------------------------------------+
                                  |          FastAPI Backend              |
                                  +---------+-------------------+---------+
                                            |                   |
                  +-------------------------+                   +-------------------------+
                  |                                                                       |
                  v                                                                       v
+------------------------------------+                                  +------------------------------------+
|         Skill-Gap Engine           |                                  |        Embedding Engine            |
| - Target Role vs Current Skills    |                                  | - sentence-transformers            |
| - Job Description Skill Extractor  |                                  | - all-MiniLM-L6-v2 (384-dim)       |
+-----------------+------------------+                                  +-----------------+------------------+
                  |                                                                       |
                  | Missing Skills                                                        | Query Embedding
                  +-----------------------------------+-----------------------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |     Vector Retrieval & Search         |
                                  |  - Supabase PostgreSQL (pgvector)     |
                                  |  - Local In-Memory Cosine Fallback    |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  |       Multi-Factor Re-Ranking         |
                                  | Final = 50% Sem + 20% Role +          |
                                  |         10% Skill + 10% Diff +        |
                                  |         10% Goal Match                |
                                  +-------------------+-------------------+
                                                      | Top-K Resources
                                                      v
                                  +---------------------------------------+
                                  |      Context Construction & RAG       |
                                  | - Strict Anti-Hallucination Prompt    |
                                  | - Hugging Face Inference LLM          |
                                  +-------------------+-------------------+
                                                      |
                                                      v
                                  +---------------------------------------+
                                  | Grounded Recommendation & Roadmap     |
                                  | - "Why Recommended" Evidence          |
                                  | - Verified URLs & Durations           |
                                  | - Structured 3-Month Plan             |
                                  +---------------------------------------+
```

---

## 5. Technology Stack
- **Frontend**: React 18, Vite, Lucide Icons, Vanilla CSS (Modern Dashboard Design System)
- **Backend**: Python 3.11, FastAPI, Uvicorn, Pydantic v2
- **Vector Database**: Supabase PostgreSQL with `pgvector` extension
- **Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors)
- **LLM Synthesis**: Hugging Face Inference API (`meta-llama/Llama-3.2-3B-Instruct` or `Qwen/Qwen2.5-7B-Instruct`)
- **Testing & Evaluation**: Pytest, Precision@K, Recall@K, Groundedness Score

---

## 6. Database Structure
The project uses two primary relational tables in PostgreSQL:

### `resources` Table
| Column | Type | Description |
| :--- | :--- | :--- |
| `id` | SERIAL PRIMARY KEY | Unique resource identifier |
| `title` | VARCHAR(255) | Title of the learning resource |
| `description` | TEXT | Detailed description of covered concepts |
| `skill` | VARCHAR(100) | Primary skill taught (e.g. SQL, Python) |
| `role` | VARCHAR(100) | Target industry role |
| `difficulty` | VARCHAR(50) | Beginner / Intermediate / Advanced |
| `type` | VARCHAR(50) | Course / Video / Tutorial / Book / Practice |
| `duration` | VARCHAR(50) | Estimated completion time (e.g. 10 hours) |
| `provider` | VARCHAR(150) | Educational provider (e.g. Coursera, freeCodeCamp) |
| `url` | TEXT | Verified public URL |
| `career_goal` | VARCHAR(100) | Placement / Job / Internship / Certification |
| `content` | TEXT | Deep curriculum / syllabus details |
| `verified` | BOOLEAN | Verification status badge |
| `embedding` | vector(384) | Dense vector embedding from MiniLM |
| `created_at` | TIMESTAMPTZ | Creation timestamp |

### `career_roles` Table
Stores standard role blueprints with `role_name`, `description`, and `required_skills` (PostgreSQL `TEXT[]` array).

---

## 7. Embedding Process
Each resource is converted into a rich textual representation:
```python
text = f"{title} | {description} | Skill: {skill} | Role: {role} | Difficulty: {difficulty} | Goal: {career_goal} | Syllabus: {content}"
```
The model `sentence-transformers/all-MiniLM-L6-v2` encodes this into a 384-dimensional normalized vector stored in the `embedding` column.

---

## 8. Vector Search
Cosine similarity is calculated via pgvector's cosine distance operator `<=>`:
$$\text{Similarity} = 1 - (\text{resource.embedding} \Leftrightarrow \text{query.embedding})$$
An HNSW index (`hnsw (embedding vector_cosine_ops)`) enables sub-10ms nearest neighbor retrieval over large datasets.

---

## 9. Ranking Formula
Candidate resources are ranked using a configurable multi-factor formula:
$$\text{Final Score} = w_{\text{sem}} \cdot S_{\text{sem}} + w_{\text{role}} \cdot S_{\text{role}} + w_{\text{skill}} \cdot S_{\text{skill}} + w_{\text{diff}} \cdot S_{\text{diff}} + w_{\text{goal}} \cdot S_{\text{goal}}$$
- **Semantic Similarity ($w_{\text{sem}} = 0.50$)**: Vector distance between query and resource text.
- **Role Match ($w_{\text{role}} = 0.20$)**: Aligned with chosen target career role.
- **Skill Match ($w_{\text{skill}} = 0.10$)**: Boosted if covering an identified missing skill gap.
- **Difficulty Match ($w_{\text{diff}} = 0.10$)**: Matching user level (Beginner/Intermediate/Advanced).
- **Career Goal Match ($w_{\text{goal}} = 0.10$)**: Placement, Job, Internship, or Certification.

---

## 10. LLM Generation & Anti-Hallucination
The prompt explicitly instructs the LLM:
1. Use ONLY the retrieved context.
2. Never invent resources, providers, durations, or URLs.
3. Cite the exact provided URLs.
4. If context is insufficient, explicitly declare that sufficient verified information was not found.

---

## 11. Skill-Gap Analysis
Given a target role (e.g. `Data Analyst`) with required skills:
- $\text{Required} = \{\text{SQL, Excel, Power BI, Statistics, Python}\}$
- $\text{User Skills} = \{\text{Excel, Python}\}$
- $\text{Known Skills} = \text{Required} \cap \text{User} = \{\text{Excel, Python}\}$
- $\text{Missing Skills} = \text{Required} \setminus \text{User} = \{\text{SQL, Power BI, Statistics}\}$

The RAG pipeline prioritizes retrieving resources matching the missing skills set.

---

## 12. API Documentation

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/health` | Service health, Supabase status, and catalog count |
| `GET` | `/api/roles` | List all predefined career roles and required skills |
| `GET` | `/api/resources` | List all verified resources from knowledge base |
| `POST` | `/api/skill-gap` | Compute known vs missing skills |
| `POST` | `/api/analyze-job-description` | Extract skills from job description text |
| `POST` | `/api/recommend` | Complete end-to-end RAG recommendation pipeline |

---

## 13. Installation

### Prerequisites
- Python 3.10 or 3.11
- Node.js 18+ and npm

### Backend Setup
```bash
cd career-rag/backend
python -m venv venv
# On Windows PowerShell:
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### Frontend Setup
```bash
cd career-rag/frontend
npm install
```

---

## 14. Environment Variables
Copy `.env.example` to `.env` in `career-rag/backend/`:
```bash
cp .env.example .env
```
Fill in:
```env
SUPabase_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key
HUGGINGFACE_API_KEY=hf_your_key_here
HF_LLM_MODEL=meta-llama/Llama-3.2-3B-Instruct
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

---

## 15. How to Run Frontend
```bash
cd career-rag/frontend
npm run dev
```
The frontend dashboard will be available at `http://localhost:5173`.

---

## 16. How to Run Backend
```bash
cd career-rag/backend
uvicorn main:app --reload --port 8000
```
Interactive Swagger docs: `http://localhost:8000/docs`.

---

## 17. How to Add New Resources
1. Open `career-rag/data/resources.csv`.
2. Append a new row with verified details and an authentic URL.
3. Run the ingestion script (when configured):
   ```bash
   python ingest.py
   ```
   This generates the 384-dimensional embedding and pushes it to Supabase.

---

## 18. How to Deploy
- **Database**: Free tier Supabase project with `pgvector`. Run `backend/database.sql` in the Supabase SQL Editor.
- **Backend**: Deploy container to Render, Railway, or Fly.io with Python 3.11.
- **Frontend**: Deploy Vite build to Vercel, Netlify, or Cloudflare Pages.

---

## 19. Limitations
- Embedding model covers 384 dimensions optimized for short-to-medium text.
- Knowledge base contains curated verified courses; does not scrape arbitrary untrusted websites.
- Free Hugging Face inference tokens have rate limits; offline hybrid fallback mode ensures zero demo crashes.

---

## 20. Future Improvements
- Multi-modal support for video lecture summarization.
- Automated web crawler with URL validator and link freshness checking.
- User authentication and persistent progress tracking across months.
- Adaptive quiz assessment to verify student skill level objectively.
