# Dataset Audit (Phase 1, Steps 01–02)

Audit date: 2026-10-05. Everything below was read from the files as downloaded; no column,
row or value is assumed. Where a column's *meaning* is not stated in the file itself it is
marked **inferred** and must be confirmed against the companion paper before use.

Provenance, hashes and licences: `data/metadata/datasets.json`. Loaders and schema checks:
`utils/datasets.py`, `tests/test_datasets.py`.

| | Pharma | Energy |
|---|---|---|
| File | `data/raw/pharma/Table 1.xls` | `data/raw/energy/Case_Study_OptiREC.xlsx` |
| Source | figshare 6971474, v1 | Mendeley Data bvp4vrn9gc, v1 (published 2025-05-02) |
| DOI | 10.1371/journal.pone.0201604.t001 | 10.17632/bvp4vrn9gc.1 |
| Size | 9,728 bytes | 6,535,061 bytes |
| SHA-256 | `7f389937…5eaa470` | `b61c6049…17ed09a` |
| Repository checksum | MD5 matches figshare | SHA-256 matches Mendeley |
| Licence | CC BY 4.0 | CC BY 4.0 |

---

## 1. Pharmaceutical dataset

### 1.1 What the file actually is

One sheet, `Table 1`, **25 rows × 3 columns**: a header row plus **24 rows, one per
sub-criterion**. It is Table 1 of Forghani, Sadjadi & Farhang Moghadam (2018), *A supplier
selection model in pharmaceutical supply chain using PCA, Z-TOPSIS and MILP: A case study*,
PLOS ONE, doi:10.1371/journal.pone.0201604.

| Column (as in file) | dtype | Type | Content |
|---|---|---|---|
| `Main Criteria` | text | categorical, 6 levels | merged cells; filled only on the first row of each group |
| `Sub-criteria` | text | identifier | `c1` … `c24`, wrapped in HTML/MathML markup |
| *(unnamed third column)* | text | free text | the sub-criterion name |

Contents (complete):

| Main criterion | Sub-criteria |
|---|---|
| Cost (3) | c1 product price; c2 payment terms; c3 delivery cost |
| Quality (5) | c4 product quality; c5 number of defective items; c6 packaging and labeling; c7 ISO 9001; c8 research, development and innovation |
| Services (2) | c9 customer relationship management (CRM); c10 after-sales service/warranty |
| Delivery (2) | c11 geographical location; c12 on-time delivery |
| Supplier profile (10) | c13 financial status; c14 management and organization; c15 technical ability; c16 facilities; c17 capacity; c18 past record documentation; c19 GMP certificate; c20 ISO 14001; c21 OHSAS 18001; c22 risk assessment system |
| Overall personnel capabilities (2) | c23 labor overall skills; c24 labor experience |

- **Unit of observation:** a *selection criterion*. Not supplier-level, not company-level,
  not transaction-level.
- **Numerical variables:** none. **Categorical/text:** all three columns.
- **Missing values:** 18 of 24 `Main Criteria` cells are empty because of merged cells
  (structural, not missing data; forward-filled by the loader). No other empty cells.
- **Duplicates:** none. **Outliers:** not applicable (no numeric values).
- **Formatting:** cells carry HTML tags (`<b>`, `<i>`, `<sub xmlns:mml=…>`); the loader strips
  them in memory. The raw file is untouched.
- **Licence / citation:** CC BY 4.0; cite the figshare item and the PLOS ONE article.

### 1.2 Gap P-1 (blocking): the primary pharma file contains no observations

The mechanism needs suppliers with measured attributes, a reference decision, and enough
scenarios to train five SHAP-compatible models. The file provides **none** of these: no
suppliers, no cost/quality/delivery/risk/compliance values, no decisions. It cannot support
Phases 3–8 on its own, and Golden Rules 1–2 forbid filling the hole with invented data.

### 1.3 What real pharma data the source study does publish

To size the gap, the other ten tables of the same article were downloaded from figshare
(all CC BY 4.0, MD5-verified) into `data/raw/pharma_paper_tables_candidate/`. **They are not
part of the primary dataset; adopting them is a user decision.**

| Table | Shape | Content |
|---|---|---|
| 2 Questionnaire | 24 criteria × 34 respondents (`x1`…`x34`) | integer importance scores 0–10; no missing; 1 duplicated respondent column; c19 (GMP) is 10 for every respondent (zero variance) |
| 3, 4, 5 | 7 rows each | linguistic scales → triangular fuzzy numbers (criterion importance; alternative rating; expert reliability) |
| 6 | 4 criteria × 2 decision makers | importance + reliability (linguistic) for the 4 criteria retained after PCA: product quality, product price, past record documentation, CRM |
| 7, 8 | 4 suppliers × 4 criteria, one table per decision maker | linguistic rating + reliability (Z-number) for each supplier/criterion |
| 9 | 4 suppliers | Z-TOPSIS closeness coefficient and rank (S2 0.635 > S3 0.526 > S1 0.474 > S4 0.354) |
| 10, 11 | 4 criteria / 4 suppliers × 7 weight cases | sensitivity analysis of weights and resulting closeness coefficients |

Observations from these tables (not from the article text, which has not yet been read):
tables 7–8 use a rating label `F` that does not appear in the Table 4 scale (which has `M`,
Medium) — needs checking against the article. No table carries MILP inputs (prices, demand,
capacities); whether the article body publishes them is **unverified**.

So the **entire real supplier-level evidence of the study is 4 suppliers × 4 criteria × 2
decision makers** (32 ratings, each with a reliability label), plus 34 questionnaire
respondents' importance scores for 24 criteria, and a published ranking that can be reproduced.

### 1.4 Pharma gaps against the mechanism

| Need | Available? | Status |
|---|---|---|
| Supplier-level observations | Not in primary file. 4 suppliers in paper Tables 7–8 | **open — user decision** |
| Cost variable | Only "product price" as a linguistic rating (Tables 7–8); c2, c3 unobserved per supplier | open |
| Quality variable | "Product quality" linguistic rating; c5–c8 unobserved per supplier | open |
| Logistics / delivery variable | **Absent** per supplier (c11, c12 appear only as criteria names and questionnaire importances). Nearest real variable: CRM (service) | open |
| Risk / reliability variable | No risk rating per supplier (c22 name only). Nearest: "past record documentation"; also the Z-number *reliability* attached to each rating | open |
| Compliance variable | **Absent** per supplier (c7, c19–c21 names only) | open |
| Reference decision / ground truth | Table 9 Z-TOPSIS ranking + Tables 10–11 sensitivity (reproducible) | available if candidate tables are adopted |
| Enough scenarios for ML training and ≥5-seed statistics | 4 suppliers; no natural train/val/test split | **open — forces a design change** |

No gap has been resolved by derivation or simulation. Options are listed in §3.

---

## 2. Energy dataset

### 2.1 Structure

One workbook, five sheets. **No missing values in any sheet.** The file contains no data
dictionary, units, or description sheet. Repository description: "annual input data used in
the study *Statistical Analysis of an Energy Community's Operations in P2P Energy Trading and
Flexibility Markets*… hourly electricity demand, PV generation, thermal profiles, and DER
configurations for 55 users in a low-voltage distribution network."

| Sheet | Rows × cols | Unit of observation | Duplicated rows |
|---|---|---|---|
| `Buses` | 206 × 22 | network bus (55 of them host a user) | 0 |
| `Profiles` | 8760 × 121 | hour of one year (time series) | 0 |
| `EV_Parameters` | 8760 × 9 | hour of one year | 8757 (a repeating daily pattern, not an error) |
| `Lines` | 410 × 14 | directed line record (205 physical lines, each listed in both directions) | 0 |
| `Adj_Matrix` | 206 × 207 | bus × bus adjacency (first column = bus id) | n/a |

All variables are numerical; binary flags are noted. There are no free-text or multi-level
categorical columns.

### 2.2 `Profiles` (8760 hourly rows)

`Hour` runs 1…8760, unique and monotone. There is **no calendar date, year, or timezone**
in the file.

| Column | dtype | Range (min – max), mean | Meaning |
|---|---|---|---|
| `Hour` | int64 | 1 – 8760 | hour index |
| `PG_max` | float64 | 0 – 1, 0.181 | **inferred:** normalised PV availability profile |
| `PG_max_Original` | float64 | 0 – 1, 0.138 | **inferred:** an earlier/unadjusted PV profile (corr. 0.72 with `PG_max`); relation undocumented |
| `Price` | float64 | 11.68 – 954.01, 287.29 | **inferred:** electricity purchase price; unit not stated |
| `Price_SG` | float64 | 0 – 702.60, 167.02 | **inferred:** price for selling to the grid; ≤ `Price` in every hour; 18 zero hours |
| `Gas_Price` | float64 | 11.79 – 245.00, 99.15 | **inferred:** gas price; unit not stated |
| `Temperature` | float64 | 0.94 – 30.64, 16.08 | **inferred:** ambient temperature, °C |
| `TL_Flex_Availability` | int64 (binary) | 0/1, 0.75 | 0 in hours 0–5 of each day, 1 otherwise; **inferred:** thermal-load flexibility window |
| `Beneficio` | float64 | −4.25 – 748.66, 210.50 | Spanish "benefit"; definition undocumented |
| `Costo` | float64 | 16.26 – 1210.53, 325.39 | Spanish "cost"; definition undocumented |
| `Th_Factor` | float64 | −461.87 – −9.99, −114.88 | equals `Beneficio − Costo` exactly (verified); purpose undocumented |
| `P_<bus>` × 55 | float64 | 0.032 – 1.0, 0.397 | **inferred:** normalised electrical demand of the user at that bus (each column peaks at 1.0) |
| `Th_<bus>` × 55 | float64 | 0 – 0.00748, 0.0004 | **inferred:** thermal demand profile; 71.4% of values are zero |

Findings that matter for design:

- **Demand profiles are not 55 independent series:** only **22 distinct `P_` columns** and
  only **3 distinct `Th_` columns** exist; the rest are exact copies. Users sharing a profile
  are related observations — relevant for leakage control and for effective sample size.
- Profiles are **normalised shapes**, to be scaled by per-bus capacities in `Buses`.
- **Outliers (1.5×IQR rule, descriptive only — nothing removed):** `Price` 265, `Price_SG`
  224, `Gas_Price` 408, `Beneficio` 378, `Costo` 264, `Th_Factor` 206, `PG_max` 321,
  `PG_max_Original` 951 (zero-inflated night hours make the rule over-flag PV), `Temperature`
  0. Across `P_` columns 3,727 of 481,800 values are flagged. Price spikes up to 954 look
  like genuine market spikes rather than errors; **no value is impossible** (no negative
  demand, PV or price).

### 2.3 `Buses` (206 rows)

MATPOWER-style bus table plus DER columns. Constant columns: `type`=1, `QL`=0, `area`=1,
`Vm`=1, `Va`=0, `baseKV`=0.4, `zone`=1.

| Column | dtype | Observed values | Meaning |
|---|---|---|---|
| `bus_i` | int64 | 1…206 | bus id |
| `PL` | float64 | 0 or 0.0034 (55 buses) | **inferred:** peak active load (MW ⇒ 3.4 kW), **identical for all 55 users** |
| `Vmax`, `Vmin` | float64 | 1.01 / 0.9 (bus 1: 1.0 / 1.0) | voltage limits (p.u.) |
| `DG` | float64 | 0, 0.005, 0.007, 0.008 (31 buses > 0) | **inferred:** PV capacity |
| `BT` | float64 | 0, 0.0055, 0.0077, 0.0088 (16 buses > 0) | **inferred:** battery capacity |
| `E_BT` | int64 (binary) | 16 ones | battery present |
| `P_SG_max`, `P_BG_max`, `THmax` | int64 | 4 at bus 1, else 0 | **inferred:** limits of exchange with the upstream grid at the slack bus |
| `Th_Load` | int64 (binary) | 55 ones | user has thermal load |
| `EV` | int64 (binary) | 3 ones (buses 10, 133, 177) | EV present |
| `PSI_EV` | float64 | 0 or 0.024 | **inferred:** EV battery parameter |
| `HP_Max` | float64 | 0 or 0.003 (55 buses) | **inferred:** heat-pump capacity |
| `Boiler_Max` | float64 | 0, 0.003, 0.005, 0.008 (48 buses > 0) | **inferred:** boiler capacity |

User composition: 55 users; 31 with PV (prosumers), 24 without; 16 with a battery (all of
them also have PV); 3 with an EV. The `P_`/`Th_` column ids equal exactly the buses with
`PL > 0` (verified).

### 2.4 `EV_Parameters`, `Lines`, `Adj_Matrix`

- `EV_Parameters`: `H_<bus>` (binary; 1 during hours 0–8 and 19–23 of each day — **inferred:**
  EV at home), `SOC_min_EV_<bus>` (0.1, with 0.7 at hour 7 for buses 10 and 133; constant 0.1
  for 177), `SOC_max_EV_<bus>` (constant 0.9). Deterministic daily pattern, identical every day.
- `Lines`: `fbus`, `tbus`, `r`, `x`, `Smax` vary; `b`, `rateA/B/C`, `angle` = 0, `ratio` = 1,
  `status` = 1, `angmin/angmax` = ∓360 are constant. `Smax` 0.079 – 0.647.
- `Adj_Matrix`: symmetric 0/1, 205 edges on 206 buses ⇒ a radial (tree) feeder, consistent
  with `Lines`.

### 2.5 What the energy dataset lacks

| Need | Available? | Proposed handling |
|---|---|---|
| Hourly demand per user | Yes (`P_*` × `PL`) | use; (b) mapped |
| PV generation per prosumer | Yes (`PG_max` × `DG`) — one shared irradiance shape for all prosumers | use; (b) mapped |
| Prices | Yes (`Price`, `Price_SG`, `Gas_Price`) — units to confirm | use; (b) mapped |
| Grid constraints | Yes (`Lines.Smax`, voltage limits, slack-bus exchange limits) | use; (b) mapped |
| Storage parameters | Capacity/SOC *limits* only (`BT`, EV SOC bounds). **No efficiencies, charge-rate limits, or initial SOC found** | open: take from the companion paper if published there; otherwise (c) with stated assumption |
| **Observed storage dispatch / SOC trajectories** | **Absent** | (c) must be derived by a transparent rule or optimisation; labelled *derived* |
| **Observed P2P trades, matched volumes, clearing prices** | **Absent** — the file is *input* data to an optimisation model; no model outputs are included | (c) reference allocation must be **constructed** (transparent optimisation/rule) and labelled a *constructed reference*, with sensitivity analysis |
| P2P internal price | Absent | (c) derive from `Price`/`Price_SG` (e.g. a mid-market rule) — labelled derived; rule to be fixed in the protocol |
| Calendar (weekday, month, holidays) | Absent; only hour index | derive hour-of-day/day-index from `Hour`; do not assume a start weekday |
| Data dictionary / units | Absent | confirm from companion paper before Phase 9 |
| Measurement provenance | The file does not say whether profiles are metered or modelled; 22 distinct demand shapes and 3 thermal shapes for 55 users suggest representative/replicated profiles | **must be verified in the companion paper**; if modelled, the paper must not call them metered household data |

None of the (c) items has been implemented. Each will be fixed in `docs/research_protocol.md`
before use.

---

## 3. Design consequences

1. **Energy:** the five conceptual roles (Producer, Consumer, Price/Market, Grid, Storage)
   all map to real columns. The decision being learned (who trades/charges what) is not
   observed, so the ground truth is a *constructed reference* in this domain.
2. **Pharma (blocking, Gap P-1):** the specified dataset cannot support the pharma case
   study. Options, for the user to choose:
   - **A — adopt the source study's Tables 2–11 as the real pharma data.** All real, CC BY,
     published ranking reproducible (Step 07). Limits: 4 suppliers and 4 rated criteria, so
     at most four agents have a distinct real supplier-level objective (price, quality, CRM
     service, past record); a fifth could use the real Z-number *reliability* labels, but
     delivery and compliance agents are **not** supportable. Scenarios would have to be
     built by recombining real elements (34 respondents' weights × 2 decision makers ×
     supplier subsets) — real values, but strongly dependent observations and a tiny
     supplier pool, which limits statistical claims.
   - **B — replace or supplement with a different real supplier-level pharma dataset** chosen
     by the user (the only route to five distinct real-variable agents with ordinary
     train/test splits).
   - **C — run the energy case study first** and defer pharma until A or B is settled
     (reorders CLAUDE.md phases; the Critical Checkpoint would be evaluated on energy).
   - Simulating supplier attributes for the 24 criteria is **not** offered as an option: it
     would make the pharma case study synthetic, contrary to Golden Rule 1.

---

## 4. Candidate pharma dataset supplied by the user: `pharma-data.csv` (audited 2026-10-05)

Audited from a byte-identical copy of `C:\Users\Ahsan\Desktop\archive (1)\pharma-data.csv`
(SHA-256 `1f9aeaaa48842241378ebdc1482651ec55df8b05b07eccfe2919356905d7d412`; 45,450,412
bytes). The project copy was removed afterwards because drive C: ran out of space; the
original stays where the user put it and is not in `data/raw/` or git.

**Provenance, licence and citation are unknown.** One web search for the file name and its
column names did not identify a source. The folder name suggests a Kaggle archive download.
Until the user supplies the source URL, licence and author, this file cannot be cited and
Phase 1 step 2 (metadata) is incomplete for it.

### 4.1 Structure

254,082 rows × 18 columns. No missing values, no blank strings.

| Column | dtype | Type | Distinct | Notes |
|---|---|---|---|---|
| `Distributor` | text | categorical | 29 | trailing whitespace in 253,005 rows (same 29 after stripping) |
| `Customer Name` | text | categorical | 751 | trailing whitespace in 41,261 rows |
| `City` | text | categorical | 749 | one city per customer; effectively the same variable as customer |
| `Country` | text | categorical | 2 | Germany 213,598; Poland 40,484 |
| `Latitude`, `Longitude` | float | numeric | 655 / 709 | city coordinates |
| `Channel` | text | categorical | 2 | Pharmacy / Hospital |
| `Sub-channel` | text | categorical | 4 | nested: Hospital→Government/Private, Pharmacy→Institution/Retail |
| `Product Name` | text | categorical | 240 | |
| `Product Class` | text | categorical | 6 | one class per product |
| `Quantity` | float | numeric | 1,735 | min −7,200, median 20, max 117,600; 2,633 negative, 27 zero, 36 non-integer |
| `Price` | int | numeric | 210 | 22 – 794; **exactly one price per product** in all years, countries, distributors |
| `Sales` | float | numeric | 20,546 | equals `Quantity × Price` in 100% of rows (no independent information) |
| `Month`, `Year` | text / int | time | 12 / 4 | 2017–2020, all 48 months present |
| `Name of Sales Rep` | text | categorical | 13 | |
| `Manager`, `Sales Team` | text | categorical | 4 / 4 | determined by the sales rep |

- **Unit of observation:** one monthly sales line: distributor × customer × product × month
  (99% of such combinations have exactly one row). Transaction-like, but there is no order
  id, date within the month, or delivery record.
- **Duplicates:** 4 exact duplicate rows.
- **Outliers (not removed):** quantities are heavily right-skewed (99th percentile 1,600;
  maximum 117,600); the five largest lines all belong to one distributor in August 2019.
  Negative quantities (1.0%) look like returns/credit notes, concentrated in three distributors.
- **Coverage is uneven:** 2018 has 94,434 rows against 51–56 thousand in other years. All
  40,484 Polish rows, all 200 Polish customers and 13 of the 29 distributors exist **only in
  2018**. Three distributors account for 77% of rows; 14 distributors appear in one year only.

### 4.2 Is it real data? — evidence that it is synthetic or heavily masked

1. **Generated names.** Distributors and customers are surname combinations in the style of
   the Faker library ("Gottlieb-Cruickshank", "Zieme, Doyle and Kunze", "Kozey-Emmerich").
   Product names are invented compounds ("Topipizole", "Choriotrisin").
2. **Fields are statistically independent of each other.** With 254,082 rows, Cramér's V is
   0.005–0.011 (all p > 0.1) for product class × distributor, product class × channel,
   product class × country, sales rep × distributor/class/country. Real markets do not
   behave this way (hospital and pharmacy product mixes differ; reps have territories).
3. **Sales reps are assigned uniformly at random:** each of 13 reps has 19.4–19.7 thousand
   rows and every one of the 751 customers is served by all 13 reps.
4. **Prices carry no behaviour:** one constant price per product for four years in two
   countries; Spearman correlation between price and quantity is −0.001.
5. Share of variance of log(quantity) explained by each field alone (positive rows):
   distributor 11.9%, customer/city 4.4%, country 4.1%, year 1.5%, month 0.1%, product name
   0.1%, **channel, sub-channel, product class, sales rep and sales team ≈ 0.0%**.

Quantities themselves look plausible (round pack sizes, returns, country differences), so
the file may be real volumes with all labels randomised, or fully generated. **Either way it
must not be described as real-world observational pharma data** unless its source says so,
and CLAUDE.md Golden Rule 1 ("real data is the primary evidence") is not met by it as it
stands.

### 4.3 Gaps against the mechanism

| Need | Available? |
|---|---|
| Supplier/distributor quality, delivery time, risk, compliance | **Absent** |
| Cost | Only list price per product (constant); no purchase cost, margin or logistics cost |
| Decision/outcome label | **Absent** — no "chosen" or "optimal" option, no service outcome |
| Demand | `Quantity` per distributor × customer × product × month (usable) |
| Geography | Coordinates of customers; **no distributor location**, so no distance can be computed |
| Predictive structure for five distinct agents | Weak: only distributor, customer/country and year relate to quantity. A channel-based or product-class-based agent would have **no signal** (item 5 above) |

### 4.4 Consequences for the design proposed with the file

The proposal (Demand, Pricing, Distribution, Market, Product agents choosing a
distributor/product/channel combination) is not supported as stated:
- A **Pricing** agent has a constant per product and `Sales` is a product of two other columns.
- **Market** (channel) and **Product** (class) agents would explain none of the outcome, so
  their SHAP explanations would be attributions of noise.
- "Which distributor should be selected" has no ground truth: nothing in the file says a
  distributor performed well or badly, and product/channel/distributor are independent.
- Any reference decision would have to be built almost entirely from assumptions, on top of
  data that is itself probably synthetic.

Nothing has been built on this file. Options are in the research log (2026-10-05 entry).
