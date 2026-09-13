# Ivy Homes — Property Discovery & Intelligence

A property discovery web application built for the Ivy Homes Software Engineering Internship assignment.

The application provides authenticated property browsing for Gurgaon, with listings, rentals, projects, saved properties, listing details, and an insights dashboard backed by the Ivy Homes API.

## Features

- **Authentication**
  - Real email/password login through the Ivy Homes API.
  - Bearer-token based authenticated requests.
  - Session persisted across page refreshes.
  - Invalid/expired sessions redirect to login.

- **Listings**
  - Offset-based pagination using the behavior of the running API.
  - Filters for locality, BHK, furnishing, minimum price, and maximum price.
  - Sorting by price, area, bedroom count, and posted date.
  - Live-only filtering.
  - Global descending price sorting is handled client-side because the API ignores the documented sort direction.

- **Listing Details**
  - Every listing has a dedicated URL.
  - Displays price, area, BHK, furnishing, floor, verification status, and description.

- **Saved Listings**
  - Add/remove listings from the authenticated user's saved collection.
  - Saved state persists across reloads and re-login.
  - Uses the working `/v1/saved` API discovered during investigation.

- **Rentals**
  - Browse rentals with locality, BHK, and furnishing filters.
  - Displays monthly rent and deposit.

- **Projects**
  - Browse projects with locality and project status.
  - Displays project pricing, units, and availability.

- **Insights**
  - Assignment-specific data analysis.
  - Displays the computed answers and useful API/data-quality discoveries.
  - Highlights anomalies found while independently validating the API.

## Tech Stack

- React
- Vite
- JavaScript
- CSS
- Fetch API
- Ivy Homes REST API

## Running Locally

### Prerequisites

- Node.js
- npm
- Ivy Homes assignment API key

### Installation

```bash
npm install
```

Create a `.env` file in the project root:

```env
VITE_API_BASE_URL=https://solve.ivy.homes
VITE_API_KEY=your_api_key_here
```

Do not commit the real API key.

Start the development server:

```bash
npm run dev
```

### Verification

```bash
npm run lint
npm run build
```

Both checks were run successfully during development.

## API Investigation

The supplied `API_REFERENCE.md` explicitly states that it was drafted by AI, had not been reviewed against the running service, and may contain outdated or incorrect information.

The implementation therefore treats the **running API as the source of truth**.

The API was independently investigated for authentication, pagination, listing lifecycle, filtering/sorting, secondary endpoints, timestamps, duplicates, project consistency, and data-quality anomalies.

### Important API discrepancies

| Area | Documented | Observed | Implementation |
|---|---|---|---|
| Authentication | API key via `?api_key=...` | Query parameter is rejected; key must use `X-API-Key` | Central API client sends `X-API-Key` |
| Pagination | `page` + `limit` | `page` is ignored; `offset` + `limit` controls pagination | Frontend uses offset pagination |
| Listings | `/v1/listings` returns active listings only | Inactive records are also returned; `is_live` is present | UI exposes Live-only filtering |
| Listing total | API reports `3375` | Full pagination returned `3500` | Investigation paged to the end |
| Rentals total | API reports `1273` | Full pagination returned `1320` | Investigation paged to the end |
| Projects total | API reports `386` | Full pagination returned `400` | Investigation paged to the end |
| Sorting | `order` controls direction | `asc` and `desc` both returned ascending price | Descending price is globally sorted in the client |
| Saved listings | Docs describe `/v1/favourites` | `/v1/favourites` is unavailable; `/v1/saved` works | Frontend uses `/v1/saved` |
| Analytics | `/v1/analytics/summary` documented | Endpoint returned `404` | Insights are computed from retrieved data |
| Project counts | `total_listings` should agree with listings | 295 of 400 retrieved projects mismatch | Insights report the inconsistency |
| Project prices | Documented as rupees | Observed project price values use a different numeric convention | Values were independently interpreted and verified |
| Timestamps | Documentation specifies UTC `Z` | Health reports `Asia/Kolkata`; listing timestamps lack `Z` | Raw timestamps are handled explicitly |
| Duplicate properties | Each listing describes one physical property | One strong duplicate-property fingerprint was identified | Duplicate analysis is included in findings |

## Assignment Answers

The following values were computed from the complete retrievable dataset and the assignment rules.

| # | Question | Answer |
|---|---|---:|
| 1 | `total_listing_records` | **3500** |
| 2 | `unique_properties` | **3499** |
| 3 | `active_listings` | **2792** |
| 4 | `corrupt_listing_ids` | **100-6001475, DWE-6000627, MAG-6000014, SQU-6002204, SQU-6002405, ZER-6001341** |
| 5 | `total_monthly_rent` in Sohna Road | **₹3,733,800** |
| 6 | `avg_price_per_sqft_2bhk` | **₹26,709.99037687148 / sq ft** |
| 7 | `costliest_project` | **P60090 — ₹989,000,000 price ceiling** |
| 8 | `listings_last_7_days` | **129** |
| 9 | `fake_listing_ids` | **100-6000297, DWE-6001082, MAG-6002328, SQU-6000334, SQU-6002610, ZER-6000479** |
| 10 | `projects_with_wrong_listing_count` | **295** |

### Data interpretation notes

- Assigned city: **Gurgaon (city_id 6)**.
- Assigned locality: **Sohna Road**.
- Q2 counts distinct physical properties rather than listing records. The strongest duplicate fingerprint was:
  - `DWE-6003109`
  - `MAG-6000909`
- Q4 uses the small set of records with clearly impossible geographic coordinates rather than treating every anomaly as corrupt.
- Q9 uses the six records posted after the API's assignment reference date, `2026-09-10T00:00:00+05:30`.
- Q8 uses the literal raw timestamp window from `2026-09-03T00:00:00` inclusive to `2026-09-10T00:00:00` exclusive.
- Q6 excludes both Q4 corrupt records and Q9 fake records before calculating the mean.

## Project Structure

```text
.
├── investigation/
│   ├── analyze_corrupt_candidates.py
│   ├── analyze_listings.py
│   ├── analyze_properties.py
│   ├── fetch_data.py
│   ├── find_anomalies.py
│   ├── find_property_duplicates.py
│   ├── test_pagination.py
│   └── verify_property_identity.py
├── src/
│   ├── api/
│   ├── App.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── API_REFERENCE.md
├── statement.md
├── submission.json
├── package.json
└── vite.config.js
```

The `investigation/` scripts were used to retrieve and validate the API dataset before relying on the API documentation.

## Design Decisions

### Trust the API, not the documentation

The supplied documentation warns that it may be wrong. The application therefore follows observed API behavior where it conflicts with the documentation.

### Offset pagination

The running API uses `offset` and `limit`, despite documenting `page` and `limit`. The frontend follows the observed behavior.

### Global descending price sorting

The API accepts `order=desc` but does not actually reverse the returned order. Reversing each API page would produce incorrect global ordering.

For descending price sorting, the frontend retrieves the complete filtered result set, sorts it numerically in memory, and renders it in chunks.

### User-scoped saved listings

Saved listings are loaded from the authenticated user's saved collection rather than being stored only in browser state, so saved state survives reloads and re-login.

### Defensive data handling

The application does not assume every returned record is valid. Known anomalies are surfaced through Insights rather than silently modifying source data.

## Verification

The following were manually and programmatically checked:

- Login against the real API
- Authenticated requests
- Session persistence across refresh
- Listing pagination
- Listing filters
- Listing sorting
- Listing detail navigation
- Save/remove saved listing behavior
- Saved state after reload
- Rentals browsing
- Projects browsing
- Insights values
- Responsive UI states
- ESLint
- Production build

## If I Had Two More Days

I would prioritize:

1. Automated end-to-end tests for login, filters, pagination, details, and saved listings.
2. A backend/proxy layer so the API key is not exposed directly to the browser.
3. Better presentation of invalid/corrupt source records without hiding the underlying data.
4. Richer project/listing visualizations and additional analytical insights.
5. Stronger accessibility and keyboard-navigation testing.
6. Caching/query-state management for larger datasets and repeated navigation.
7. A reusable API-validation suite that detects documentation drift automatically.

## LLM Usage

LLM assistance was used to accelerate frontend implementation, debugging, refactoring, and review.

The API was not blindly trusted based on generated suggestions. API behavior was independently tested against the running service, and the assignment answers and discrepancies were derived from retrieved data and verification scripts.

The final implementation was manually reviewed, including pagination, sorting, saved-listing behavior, assignment calculations, and build/lint checks.

## Submission

The repository contains:

- The complete React application.
- API investigation scripts.
- `submission.json` containing the required assignment answers and findings.
- This README covering setup, architecture, API investigation, and verification.
