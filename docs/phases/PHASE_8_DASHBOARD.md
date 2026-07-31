# Phase 8 Specification: Executive Dashboard Frontend

## 🎯 End Goal
Build a modern, high-aesthetic executive frontend using Next.js, Tailwind CSS, Recharts, and React Query in `moduseti assissment_frontend/`. Provides multi-file dropzones (PDFs & CSVs), real-time KPI overview cards, interactive analytics charts, strategic transformation recommendation cards, and an interactive evidence drawer.

---

## 🛠️ Sub-Phases & Deliverables

### Sub-Phase 8.1: Next.js & Design System Setup
- Path: `moduseti assissment_frontend/`
- Tech Stack: Next.js (App router/Pages router), Tailwind CSS, Lucide icons, React Query, Recharts.
- Design Tokens: Executive dark mode palette (slate/indigo/emerald accents), modern typography, glassmorphism card containers, smooth micro-animations.

### Sub-Phase 8.2: Multi-File Upload UI Component
- Path: `moduseti assissment_frontend/upload/`
- Component `UploadDropzone.tsx`:
  - 4 designated upload slots:
    1. Company Profile PDF
    2. HR Policy PDF
    3. Sales Dataset CSV
    4. Customer Dataset CSV
  - Displays file parsing state, row/chunk counts, and upload success status badges.

### Sub-Phase 8.3: KPI Cards & Recharts Visualization Components
- Path: `moduseti assissment_frontend/charts/`
  - `RevenueTrendChart.tsx`: Recharts Area/Line chart for sales growth & revenue trends.
  - `CustomerChurnChart.tsx`: Recharts Bar/Pie chart for churn rate & CSAT scores.
  - `ExecutiveKPICards.tsx`: Metric cards (Total Revenue, YoY Growth, Churn Rate, LTV:CAC Ratio).

### Sub-Phase 8.4: Strategic Recommendations & Action Matrix
- Path: `moduseti assissment_frontend/components/`
  - `StrategicRecommendationCard.tsx`: Displays strategic issues, recommended actions, business impact, priority badge (High/Medium/Low), and expected outcome.
  - `EvidenceDrawer.tsx`: Slide-over modal showing underlying evidence citations (`source`, `category`, `confidence`, text snippet / CSV metric) when clicked.

### Sub-Phase 8.5: Dashboard Page Integration
- Path: `moduseti assissment_frontend/pages/index.tsx` (or `app/page.tsx`)
  - Uses React Query to fetch backend dashboard endpoint `POST /api/dashboard/generate`.
  - Integrates header navigation, upload section, visual KPI charts, and transformation recommendations.

---

## 🔍 Verification Criteria
1. Frontend compiles without errors (`npm run dev`).
2. Upload dropzone allows selecting and sending files to FastAPI upload endpoints.
3. Recharts components render quantitative sales & customer metrics dynamically.
4. Clicking an evidence link opens the Evidence Drawer displaying exact backing facts.
