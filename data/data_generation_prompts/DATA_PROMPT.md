# Product Data File Conventions — Supply Chain Risk Agent

Reference for generating the fake product/raw-material dataset. Follow this exactly for every product file so retrieval behaves consistently.

## 1. File structure
- One markdown file per product.
- YAML frontmatter at the top with two fields:
  - `product`: the product name, exactly as it appears in the `# Product:` header.
  - `entities`: a flat list of every real-world entity mentioned in the file (see scope rules in §4).
- Header hierarchy, always in this order:
  - `#` — Product (one per file): `# Product: <Product Name>`
  - `##` — Stage (one of exactly four): `Planning`, `Sourcing`, `Manufacturing`, `Delivery`
  - `###` — Entity-descriptive subheader, one per raw material / plant / warehouse / demand-driver group

## 2. Closed entity sets (finalized)

Use only entities from these sets, so the knowledge graph has real overlap instead of sparse, disconnected nodes. Every product/material/location combination should draw from this pool.

### Products (8)
EV Vehicle, Smartphone, Solar Panel, Bicycle, Cotton Garment, Laptop, Wind Turbine, Steel Furniture

### Raw materials (15) and which products use them
| Material | Used in |
|---|---|
| Lithium | EV Vehicle, Smartphone, Laptop |
| Cobalt | EV Vehicle, Smartphone |
| Graphite | EV Vehicle, Smartphone |
| Nickel | EV Vehicle (alternative Battery raw material — see exception below) |
| Steel | EV Vehicle, Bicycle, Wind Turbine, Steel Furniture |
| Sulfuric Acid | EV Vehicle, Smartphone |
| Silicon | Smartphone, Solar Panel, Laptop |
| Copper | Smartphone, Solar Panel, Wind Turbine, Laptop |
| Aluminum | Solar Panel, Bicycle, Laptop |
| Zinc | Solar Panel, Wind Turbine, Steel Furniture |
| Titanium | Bicycle, Laptop |
| Iron | Bicycle, Steel Furniture |
| Cotton | Cotton Garment |
| Polyester | Cotton Garment |
| Neodymium | Wind Turbine |

Steel and Copper are deliberate hub nodes (4 products each) for demonstrating cross-product concentration risk. Cotton, Polyester, and Neodymium are deliberate single-product, low-connectivity nodes for contrast.

### Locations (closed set: China and Ukraine only)
- **China**
  - Guangdong: Shenzhen, Guangzhou
  - Jiangsu: Suzhou, Nanjing
- **Ukraine**
  - Kyiv Oblast: Kyiv, Bila Tserkva
  - Lviv Oblast: Lviv, Stryi

### Exception rule
The location set is closed to China/Ukraine **except** for explicitly documented single-material exceptions used to demonstrate a specific risk pattern. Currently one exception exists:

- **Nickel** (alternative Battery raw material for EV Vehicle) is sourced from **Sulawesi, Indonesia** — outside the closed set, on purpose, to give the risk agent a genuine sole-source-outside-safe-zone case to detect. Its data differs from the other materials:
  - Price: 18,500 USD per tonne (priced per tonne, not per unit, matching how nickel actually trades)
  - Export Control Status: Restricted
  - Stock: Limited (the floor of the controlled Stock vocabulary in §6; Nickel is the only material at `Limited`, adding a second risk dimension beyond export control)

Do not add further exceptions without documenting them here.

## 3. Header vs. bullet rule (important — this was the main correction made during design)
- **Headers and subheaders carry entity context. Bullets do not.**
- `###` subheaders repeat the entity name plus a short parenthetical describing its role, e.g.:
  - `### Battery (raw material for EV Vehicle)`
  - `### Shenzhen Plant (manufactures Battery for EV Vehicle)`
  - `### Shenzhen Distribution Hub (stores Battery for EV Vehicle)`
- Bullets underneath are plain `Field: Value` — no entity name repeated in the bullet itself.
- Why: `MarkdownHeaderTextSplitter` attaches the full header path as metadata to every chunk, so entity context survives as long as a `###` section is not further split. Keep each `###` section short (4–6 bullets) so it never exceeds the recursive splitter's chunk_size and gets fragmented — if it does, the fragment loses the header-path context since there's no per-bullet redundancy to fall back on.

## 4. `entities` frontmatter — scope
Include (real-world nouns only, drawn from the closed sets in §2):
- Product names
- Raw materials and their chemical/material components
- Countries, states/provinces, cities
- Named plants, warehouses, distribution hubs

Exclude (structural/taxonomy words, never entities):
- `Planning`, `Sourcing`, `Manufacturing`, `Delivery`
- `Product`, `Raw Material`, `Manufacturing Unit`, `Warehouse`, `Demand Drivers`

## 5. Location format
`City, State/Province, Country` for any specific site (plant, warehouse), using only cities/states/countries from the closed set in §2 (except the documented Nickel exception). Each level (city, state, country) is its own separate entity in the `entities` list.
Country-only sourcing (raw material origin without a specific site) stays as just the country name.

## 6. Controlled vocabularies and Local Rules (fixed values where scoring depends on them; bounded free text where realism requires it)
- **Export Control Status**: `Regular | Restricted | Controlled | Banned`
- **Demand Rating**: `Low | Moderate | High`
- **Stock**: `High | Medium | Low | Limited` — closed vocabulary, one value per material, and **globally consistent**: the same material carries the same Stock value in every product that uses it (it is a property of the commodity, not the product). Nickel is the only material at `Limited`. Place the line directly after `Export Control Status`.
- **Local Rules**: free text, but never `None` and never omitted. Write a realistic regulation framed as a protection for nature, people, the public, consumers, or employees that also binds the company — it should constrain expansion, scheduling, emissions, or logistics. Max **50 words**. Reuse the same rule for the same city across products so retrieval stays coherent.

## 7. Units
- Currency: `<number> USD per <unit>` (e.g. `200 USD per unit`, `100 USD per tonne`)
- Capacity: `<number> <unit> per month` (e.g. `50,000 units per month`)
- Nickel is the one exception to per-unit battery-material pricing — see §2 exception rule.

## 8. Worked example (EV Vehicle — treat as the canonical template, updated to the closed China/Ukraine location set)

```markdown
---
product: EV Vehicle
entities: [EV Vehicle, Battery, Lithium, Cobalt, Graphite, Nickel, Steel, Iron, China, Ukraine, Guangdong, Shenzhen, Lviv Oblast, Lviv, Indonesia]
---

# Product: EV Vehicle

## Planning
### Demand Drivers (for EV Vehicle)
- Seasonal Demand: Peaks in Q4 due to year-end purchase incentives and tax-credit deadlines
- Natural Calamity Impact: Flooding in a key manufacturing region can suppress short-term demand while spiking long-term replacement demand
- Man-made Factors: War or a new government EV subsidy policy can rapidly shift demand up or down
- Current Demand Rating: Moderate, with a seasonal uptick expected in Q4

## Sourcing
### Battery (raw material for EV Vehicle)
- Composition: Lithium, Cobalt, Graphite
- Source Locations: Ukraine; China
- Production Site: Shenzhen, Guangdong, China
- Price: 200 USD per unit
- Export Control Status: Regular
- Stock: Medium

### Battery — Nickel Variant (alternative raw material for EV Vehicle)
- Composition: Nickel
- Source Location: Sulawesi, Indonesia
- Price: 18,500 USD per tonne
- Export Control Status: Restricted
- Stock: Limited

### Steel (raw material for EV Vehicle)
- Composition: Iron
- Source Locations: China; Ukraine
- Price: 100 USD per tonne
- Export Control Status: Regular
- Stock: High

## Manufacturing
### Shenzhen Plant (manufactures Battery for EV Vehicle)
- Location: Shenzhen, Guangdong, China
- Capacity: 50,000 units per month
- Transport Cost: 15 USD per unit, for Lithium, Cobalt, and Graphite shipped to the plant
- Local Rules: Carbon-emissions trading scheme caps annual plant output; exceeding the allowance requires buying permits or funding local abatement projects. Labor law limits weekly overtime, so extra shifts need staggered, approved scheduling.

### Lviv Plant (manufactures Steel for EV Vehicle)
- Location: Lviv, Lviv Oblast, Ukraine
- Capacity: 30,000 tonnes per month
- Transport Cost: 10 USD per tonne, for Iron shipped to the plant
- Local Rules: Martial-law logistics rules require security-cleared shipments and rail-slot bookings through Ukrzaliznytsia; missing clearances halt dispatch. Grid-rationing windows cap plant operating hours, barring round-the-clock output.

## Delivery
### Shenzhen Distribution Hub (stores Battery for EV Vehicle)
- Location: Shenzhen, Guangdong, China
- Warehouse Cost: 5,000 USD per month
- Local Rules: Fire-zone zoning caps hazardous-material inventory mass and mandates sprinklered, segregated bays; residential proximity buffers prohibit contiguous warehouse expansion.

### Lviv Distribution Hub (stores Steel for EV Vehicle)
- Location: Lviv, Lviv Oblast, Ukraine
- Warehouse Cost: 3,000 USD per month
- Local Rules: Transit-terminal access requires security passes renewed monthly, and rail-slot allocations through Ukrzaliznytsia grant westerly hubs priority only at set windows, capping throughput.
```

## 9. Fake news dataset (separate collection)

News lives in its own vector store/collection, separate from the product data store. This means there is no shared graph between the two — the link between a product's entities and a relevant news item is made by the orchestration layer, not by graph traversal. Retrieval flow:
1. Agent 1 (`GraphRetriever` on the product collection) returns a set of entities for the product being checked (e.g. `[Lithium, Ukraine, China]`).
2. Agent 2 takes that entity list and runs a hybrid/vector search against the news collection, filtered to items whose `entities` field intersects with it.
3. Agent 3 (synthesis) reasons over both result sets together.

**Critical rule: entity spelling must exactly match the closed set in §2, with no exceptions, in both collections.** There is no graph structure to route around a mismatch here — a typo or casing difference (`lithium` vs `Lithium`) silently breaks the filter and returns nothing. Treat entity names as a strict controlled vocabulary, not free text, when writing news items.

### News item template
- `event_id`: unique identifier
- `published_date`: fake date, used for recency weighting by the synthesis agent
- `entities`: real-world entities actually affected, using only closed-set spelling (§2) or the documented Nickel/Indonesia exception — geographic scope should match the event type (see below)
- `event_type`: closed vocabulary — `Natural Calamity | War/Conflict | Government Policy | Labor Dispute | Economic/Price Shock`

### Geographic scope by event type
The closed-set entities named (and the summary's stated scope) should match the kind of event — don't tag a whole country for something that's actually local, or a single city for something that's actually national:
- **Natural Calamity** — typically one region/city (e.g. flooding hits Shenzhen, not all of China)
- **War/Conflict** — typically the whole country (disrupts logistics nationwide, not just one city)
- **Government Policy** — national if issued by a central ministry, regional if issued by a provincial/state authority
- **Labor Dispute** — typically one plant or city
- **Economic/Price Shock** — can be commodity-wide (affects a material regardless of location) or regional

### Summary style
- Under 250 words. Write it like a real wire-service brief: a specific triggering event, named officials/organizations, concrete numbers and durations, a quote-like detail — enough texture that it reads as an actual news story, not a template filled in.
- `entities` is **not** restricted to the closed set in §2 — freely include company names, ministries, vessel names, specific district names, official titles, or anything else that makes the event feel real. There's no cap on how many extra entities you add.
- The one hard requirement: **the entities that actually matter for the retrieval join — the closed-set material and location affected — must still be present and spelled exactly per §2.** Everything else in the entities list is flavor and doesn't need to match anything; it just needs to sound plausible. If a closed-set entity is missing or misspelled, the retrieval join breaks silently, so double-check that part specifically.
- Vary the concrete scenario across items — don't reuse "flooding" for every calamity or "export licensing" for every policy event. Different disasters, different policy mechanisms, different labor grievances, different price triggers.

```markdown
---
event_id: news_0002
published_date: 2026-08-10
entities: [Ukraine, Lviv, Kyiv, Ministry of Infrastructure, Ukrzaliznytsia, Operation Steel Corridor]
event_type: War/Conflict
---

# News: Escalating Conflict Disrupts Ukraine-Wide Logistics

- Event Type: War/Conflict
- Location Affected: Ukraine (nationwide)
- Material Affected: Steel and Battery components sourced from Ukraine
- Date: 2026-08-10
- Summary: Renewed shelling near the M06 highway corridor has disrupted freight movement nationwide, the Ministry of Infrastructure confirmed Tuesday. State rail operator Ukrzaliznytsia reported a 30% drop in cargo throughput this week and rerouted westbound freight through Lviv under what officials are calling "Operation Steel Corridor." Shipments in and out of Lviv and Kyiv are delayed 5-10 days, with several manufacturers reporting halted deliveries of raw steel billets. Insurance underwriters have reportedly raised war-risk premiums on Ukrainian freight routes by 12% this month, further compounding logistics costs for exporters relying on rail-based delivery to western ports.
- Estimated Impact: High — expect nationwide delays across all Ukraine-sourced materials
```

```markdown
---
event_id: news_0003
published_date: 2026-08-05
entities: [China, Guangdong, Shenzhen, Longgang District Emergency Bureau, Pearl River Delta]
event_type: Natural Calamity
---

# News: Flash Flooding Shuts Down Shenzhen Manufacturing District

- Event Type: Natural Calamity
- Location Affected: Shenzhen, Guangdong, China
- Material Affected: Battery components manufactured in Shenzhen
- Date: 2026-08-05
- Summary: A record-breaking overnight downpour, tied to a stalled tropical depression over the Pearl River Delta, triggered flash flooding across Shenzhen's Longgang manufacturing belt. The Longgang District Emergency Bureau ordered several battery and electronics plants to suspend operations pending structural safety inspections, with local officials estimating a 3-5 day shutdown. Two access roads to the district remain impassable as drainage crews work to clear debris. Guangdong's broader manufacturing network outside Longgang continues operating normally, and provincial authorities say there is no indication the flooding will spread to neighboring industrial zones in the near term.
- Estimated Impact: Moderate — localized to Shenzhen's Longgang district, not provincial or national
```

```markdown
---
event_id: news_0004
published_date: 2026-08-18
entities: [Indonesia, Sulawesi, Nickel, Ministry of Energy and Mineral Resources, Morowali Industrial Park]
event_type: Government Policy
---

# News: Indonesia Expands Nickel Ore Export Restrictions

- Event Type: Government Policy
- Location Affected: Sulawesi, Indonesia
- Material Affected: Nickel
- Date: 2026-08-18
- Summary: Indonesia's Ministry of Energy and Mineral Resources announced an expansion of its nickel ore export restrictions, requiring all raw ore mined in Sulawesi to be processed domestically before export, effective next quarter. The policy builds on a 2020 ore export ban and is intended to push more smelting capacity toward the Morowali Industrial Park. Industry groups warn the move could tighten global nickel ore supply in the short term as processors outside Indonesia scramble for alternative sources. Officials say the goal is to capture more value from downstream battery-grade nickel processing rather than exporting raw material.
- Estimated Impact: High — reinforces Nickel's existing Restricted export status, tightening the supply of processed material available for battery production
```

```markdown
---
event_id: news_0005
published_date: 2026-08-22
entities: [China, Jiangsu, Suzhou, Copper, Suzhou Wire and Cable Workers Union]
event_type: Labor Dispute
---

# News: Wage Dispute Halts Copper Wire Production in Suzhou

- Event Type: Labor Dispute
- Location Affected: Suzhou, Jiangsu, China
- Material Affected: Copper
- Date: 2026-08-22
- Summary: Workers at two copper wire processing facilities in Suzhou walked off the line this week after the Suzhou Wire and Cable Workers Union rejected a proposed wage freeze tied to rising raw copper input costs. Local media report the walkout has cut regional copper wire output by roughly 20%, with management and union representatives scheduled to resume talks Thursday. Similar facilities in nearby Nanjing remain unaffected. Analysts note the dispute comes amid a broader run-up in global copper prices, which has squeezed margins for processors caught between higher input costs and fixed-price supply contracts.
- Estimated Impact: Moderate — localized to Suzhou copper wire processing, expected to resolve within 1-2 weeks
```

### Checklist for each news item
- [ ] Under 250 words, written with realistic named-source, numeric, and quote-like detail
- [ ] The closed-set material/location entities relevant to the event are present and spelled exactly per §2 — this is the one non-negotiable, since it's what makes the retrieval join work
- [ ] Freely add non-closed-set entities (companies, ministries, unions, operation names) for realism — no cap
- [ ] Geographic scope of the affected closed-set entities matches the event type (regional for calamity, nationwide for war, etc.)
- [ ] Scenario is genuinely varied from other items of the same event type — avoid reusing the same disaster/policy mechanism
- [ ] `event_type` uses the fixed vocabulary above
- [ ] `published_date` is present, for recency weighting
- [ ] At least one news item deliberately targets the Nickel/Indonesia exception, as a high-value test case for the risk agent
- [ ] Keep event-type coverage roughly balanced across the collection (the current dataset runs `news_0001`–`news_0021`, with 4 in-scope items each of Calamity/Conflict/Policy/Labor/Price plus one deliberate out-of-scope item)

## 10. Checklist for each new product file
- [ ] Product, materials, and locations are drawn from the closed sets in §2 (or the documented Nickel exception)
- [ ] Frontmatter has `product` and `entities` (entities = real-world nouns only, per §4)
- [ ] Exactly four `##` stages: Planning, Sourcing, Manufacturing, Delivery
- [ ] Every `###` subheader names its entity plus a role parenthetical
- [ ] Bullets are plain `Field: Value`, no entity name repeated inside them
- [ ] Locations use City, State/Province, Country
- [ ] Export Control Status, Demand Rating, and Stock use the fixed vocabularies in §6 (Stock present on every material, one value per material, globally consistent across products)
- [ ] Local Rules present on every plant and hub, never `None` or omitted, realistic and protective-but-constraining, ≤50 words
- [ ] Currency/capacity units follow §7 exactly
- [ ] Reuse the shared hub materials (Steel, Copper) and shared locations across products deliberately, so the graph retriever has real cross-product concentration-risk edges to find