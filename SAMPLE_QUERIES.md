# Sample Queries for the Supply Chain Risk Agent

This file contains ready-to-use queries for evaluating the agent. They are grouped by the five
user-request scenarios the main agent is designed to handle. Each query lists:

- **Query** — the exact text a user would type.
- **Agents triggered** — which of Agent 1 / 2 / 3 should be invoked.
- **Expected outcome** — what a correct answer should contain.
- **Sources** — the product files and/or news `event_id`s that back the answer.

All products, materials, locations, and news events come from the closed set defined in
`data/data_generation_prompts/DATA_PROMPT.md`. "Hub materials" (Steel, Copper) are shared across
multiple products and are the intended cross-product concentration-risk test cases.

---

## Scenario 1 — Product-data only (Agent 1)

Agent 1 searches the product knowledge base and returns the product's full supply-chain footprint
(demand drivers, raw materials, plants, warehouses, local rules, costs).

### Q1.1 — Sourcing & plans for Smartphone

> What are the raw materials needed to build a Smartphone, where do they come from, what does each cost, and what is their export-control status and stock level?

- **Agents triggered:** Agent 1
- **Expected outcome:** A list of four materials — **Battery** (Lithium, Cobalt, Graphite; China & Ukraine; Suzhou; 25 USD/unit; Regular; Medium), **Sulfuric Acid** (China; Suzhou; 8 USD/unit; Regular; High), **Silicon** (China; Nanjing; 40 USD/unit; **Controlled**; **Low**), **Copper** (China & Ukraine; 12 USD/unit; Regular; Medium). Silicon is the standout risk flag (Controlled + Low stock).
- **Sources:** `data/products/smartphone.md` (Sourcing section)

### Q1.2 — Manufacturing capacity & constraints for Laptop

> Show the manufacturing plants that build a Laptop, their capacity, transport cost, and the local rules that could constrain production.

- **Agents triggered:** Agent 1
- **Expected outcome:** Two plants — **Suzhou Plant** (Battery & Silicon; 120,000 units/mo; water-pollution permits cap output; overtime caps) and **Shenzhen Plant** (Copper/Aluminum/Titanium chassis; 100,000 units/mo; carbon-emissions trading caps output; labor overtime limits). Also list the two distribution hubs and their warehouse cost / local rules.
- **Sources:** `data/products/laptop.md` (Manufacturing, Delivery sections)

### Q1.3 — Delivery / warehouse exposure for EV Vehicle

> What warehouses does the EV Vehicle supply chain use, and what local rules could disrupt delivery or storage?

- **Agents triggered:** Agent 1
- **Expected outcome:** **Shenzhen Distribution Hub** (Battery; 5,000 USD/mo; fire-zone zoning caps hazardous inventory; no contiguous expansion) and **Lviv Distribution Hub** (Steel; 3,000 USD/mo; monthly security-pass renewals and Ukrzaliznytsia rail-slot windows cap throughput).
- **Sources:** `data/products/ev-vehicle.md` (Delivery section)

---

## Scenario 2 — Latest news only (Agent 2)

Agent 2 searches the news collection for disruption events on the requested product or entities.

### Q2.1 — Recent Copper news

> What is the latest news affecting copper supply?

- **Agents triggered:** Agent 2
- **Expected outcome:** Recent copper disruption events, most recent first:
  - **news_0005** (2026-08-22, Labor Dispute) — Suzhou copper wire walkout, ~20% output cut.
  - **news_0001** (2026-08-04, Economic/Price Shock) — LME copper +7% on smelter cutbacks.
  - **news_0010** (2026-08-09, War/Conflict) — Dnipro rail bridge damage restricts nationwide copper/zinc/aluminum shipments.
  A correct answer should surface all three touching `Copper`.
- **Sources:** `data/news/news-0001*`, `news-0005*`, `news-0010*`

### Q2.2 — Ukraine-sourced steel / logistics status

> What recent disruptions are affecting steel or battery materials sourced from Ukraine?

- **Agents triggered:** Agent 2
- **Expected outcome:** The war/conflict cluster: **news_0002** (Steel Corridor, Lviv/Kyiv delays 5–10 days), **news_0009** (Black Sea drone strikes — Steel & Polyester nationwide), **news_0011** (mobilization labor strain — Steel/Iron/Polyester), plus **news_0007** (Stryi wildfire) and **news_0006** (Guangzhou flood) if filtered by material. Should rank national war events as high impact.
- **Sources:** `data/news/news-0002*`, `news-0007*`, `news-0009*`, `news-0011*`

### Q2.3 — Bad request / no relevant news (robustness check)

> Is there any news about coffee beans?

- **Agents triggered:** Agent 2
- **Expected outcome:** Agent 2 should retrieve **news_0021** (coffee frost) but flag that `Coffee Beans` / Brazil are **outside** the tracked product/material closed set and therefore do **not** join to any of the 8 tracked products. A correct response notes this item is not actionable for this dataset.
- **Sources:** `data/news/news-0021*` (deliberate out-of-scope test case)

---

## Scenario 3 — Supply chain risk analysis (Agent 1 + Agent 2)

Agent 1 extracts the product's entities, then Agent 2 joins those entities against the news
collection; results are synthesized into a risk analysis.

### Q3.1 — Solar Panel risk analysis

> What is the supply chain risk for Solar Panel production right now?

- **Agents triggered:** Agent 1 + Agent 2
- **Expected outcome:** A risk summary across materials and stages:
  - **Silicon** — Controlled export status + Low stock (product `solar-panel.md`) compounded by no recent silicon-specific news but exposed via Guangzhou plant (below).
  - **Copper** — price +8% (news_0001) and rail capacity risk (news_0010).
  - **Aluminum** — Guangdong emissions policy (news_0013) hits aluminum smelters regionally; Bila Tserkva aluminum line paused (news_0016); Guangzhou flood hit aluminum stamping (news_0006).
  - **Zinc** — Ukraine export quota at 70% (news_0014), plus rail bridge restrictions (news_0010).
  - **Manufacturing:** Guangzhou Plant under Guangdong dual-control energy policy (product) + flood outage (news_0006); Bila Tserkva Plant subject to mandatory air-quality stoppage (product) + work stoppage (news_0016).
- **Sources:** `data/products/solar-panel.md`; `data/news/news-0001`, `news-0006`, `news-0010`, `news-0013`, `news-0014`, `news-0016`

### Q3.2 — EV Vehicle risk analysis (the Nickel test case)

> Analyze the supply chain risk for the EV Vehicle, especially around battery materials.

- **Agents triggered:** Agent 1 + Agent 2
- **Expected outcome:** The single highest-severity risk should be **Nickel** (the designed sole-source-outside-safe-zone case):
  - **Nickel** — inherent Restricted export status + Limited (only material at Limited) stock (product `ev-vehicle.md`); compounded by Indonesia ore export restriction expansion (news_0004), Sulawesi landslide halting haul road 10–14 days (news_0008), and LME nickel +9% price surge (news_0018).
  - **Battery** (Lithium/Cobalt/Graphite) — Lithium price spike +11% (news_0019); Graphite export licensing +2–3 weeks (news_0012) affecting battery-grade anode material.
  - **Steel** (Iron) — Ukraine war logistics (news_0002, news_0009, news_0010, news_0011).
  - **Manufacturing** — Lviv Plant martial-law/rail constraints (product) + war events; Shenzhen Battery plant flood exposure (news_0003).
  A strong answer should rank Nickel as the standout escalatable risk.
- **Sources:** `data/products/ev-vehicle.md`; `data/news/news-0002`, `news-0003`, `news-0004`, `news-0008`, `news-0009`, `news-0010`, `news-0011`, `news-0012`, `news-0018`, `news-0019`

### Q3.3 — Cross-product concentration risk on Copper

> Which products are at risk from the recent copper disruptions, and how severe is the shared-material exposure?

- **Agents triggered:** Agent 1 + Agent 2
- **Expected outcome:** Copper is a hub material used by **4 products**: Smartphone, Solar Panel, Wind Turbine, Laptop. A correct analysis should enumerate all four and tie them to copper-specific events: price +8% (news_0001), Suzhou wire walkout (news_0005), and rail bridge restrictions (news_0010). It may also name the alternate Nanjing copper line still running (news_0005) as partial mitigation.
- **Sources:** `data/products/smartphone.md`, `solar-panel.md`, `wind-turbine.md`, `laptop.md`; `data/news/news-0001`, `news-0005`, `news-0010`

---

## Scenario 4 — Mitigation given a supplied risk summary (Agent 3)

The user provides pre-computed risk details and asks Agent 3 to recommend mitigations.

### Q4.1 — Mitigate a tungsten/short-supply type risk (use supplied findings)

> Based on this risk summary — EV Vehicle battery depends on Nickel from Indonesia, which is export-restricted, has limited stock, and is hit by both a landslide and a price surge — what is the best course of action to mitigate this risk?

- **Agents triggered:** Agent 3
- **Expected outcome:** A prioritized mitigation plan, e.g.: (1) qualify an alternative battery chemistry that reduces nickel content (news_0018 explicitly mentions accelerating alternative chemistries); (2) secure forward contracts / re-open price-adjustment clauses (news_0018); (3) build/identify buffer stock given the 2-week regional buffer mentioned in news_0008; (4) monitor whether the domestic-processing mandate (news_0004) meaningfully shortens allocation. Agent 3 should read the relevant news (read_report/news_search) and save a report.
- **Sources:** `data/products/ev-vehicle.md`; `data/news/news-0004`, `news-0008`, `news-0018`

### Q4.2 — Mitigate a labor-dispute risk

> My analysis shows a copper wire plant in Suzhou has halted ~20% of regional output and copper prices are up 8%. What should I do?

- **Agents triggered:** Agent 3
- **Expected outcome:** Mitigations such as: (1) switch copper intake to unaffected nearby Nanjing facilities (news_0005); (2) re-open price-adjustment clauses / hedge forward copper given the price shock (news_0001, news_0005); (3) consider inventory drawdown and supplier diversification for the four copper-using products; (4) monitor next talks date for resolution window (news_0005, "talks Thursday").
- **Sources:** `data/news/news-0001`, `news-0005`

---

## Scenario 5 — Full risk analysis + mitigation (Agent 1 + Agent 2 + Agent 3)

End-to-end: retrieve product data, join with news, produce a risk analysis, and recommend actions.

### Q5.1 — Laptop full pipeline

> Give me a full supply chain risk analysis for the Laptop and recommend what to do to mitigate the biggest risks.

- **Agents triggered:** Agent 1 + Agent 2 + Agent 3
- **Expected outcome:** A complete pipeline:
  1. **Product entities** (Agent 1): Battery (Lithium, Suzhou), Silicon (Controlled, Low), Copper, Aluminum, Titanium (Controlled, Low) from `laptop.md`.
  2. **News join** (Agent 2): Lithium price spike (news_0019); Copper price (news_0001) + Suzhou copper strike (news_0005); Aluminum Guangdong policy (news_0013) + Shenzhen chassis slowdown (news_0017); Titanium chassis slowdown (news_0017); Shenzhen flood (news_0003) hitting battery components.
  3. **Risk synthesis + mitigation** (Agent 3): Core risks are the two Controlled materials — **Silicon** (export control + low stock) and **Titanium** (export control + low stock, plus active Shenzhen labor slowdown). Recommend supplier diversification, securing; buffer build for Silicon/Titanium; hedge Copper/Lithium price exposure; monitor Shenzhen labor talks.
- **Sources:** `data/products/laptop.md`; `data/news/news-0001`, `news-0003`, `news-0005`, `news-0013`, `news-0017`, `news-0019`

### Q5.2 — Wind Turbine full pipeline (multi-country exposure)

> Run a full risk analysis and mitigation plan for the Wind Turbine supply chain.

- **Agents triggered:** Agent 1 + Agent 2 + Agent 3
- **Expected outcome:**
  1. **Product entities** (Agent 1): Steel (Lviv plant), Copper, Zinc, Neodymium (Controlled, Low, Nanjing) from `wind-turbine.md`.
  2. **News join** (Agent 2): Steel/Ukraine war logistics (news_0002, news_0009, news_0010, news_0011); Copper price (news_0001) + Suzhou strike (news_0005); Zinc Ukraine export quota (news_0014); Neodymium line hit by Nanjing strike (news_0015).
  3. **Risk + mitigation** (Agent 3): **Neodymium** is the standout (Controlled + Low + active strike). Mitigations include dual-sourcing rare-earth magnets, hedging copper/zinc, and securing Ukrzaliznytsia rail slots / alternate routing for the steel lines. Also note Nanjing's reverse-logistics and waste rules bound expansion.
- **Sources:** `data/products/wind-turbine.md`; `data/news/news-0001`, `news-0002`, `news-0005`, `news-0009`, `news-0010`, `news-0011`, `news-0014`, `news-0015`

### Q5.3 — Cotton Garment full pipeline (single-product low-connectivity material)

> Analyze the Cotton Garment supply chain risk and recommend mitigations.

- **Agents triggered:** Agent 1 + Agent 2 + Agent 3
- **Expected outcome:**
  1. **Product entities** (Agent 1): Cotton (Nanjing), Polyester (Kyiv) from `cotton-garment.md`.
  2. **News join** (Agent 2): Cotton price rally +8% on crop downgrades (news_0020); Polyester/textile exposure through Ukraine war logistics (news_0009 Black Sea — Polyester; news_0011 mobilization — Polyester).
  3. **Risk + mitigation** (Agent 3): Cotton is a low-connectivity single-product node — risk is mainly price (news_0020), with the recommended hedge pivoting toward polyester blends (news_0020 explicitly notes this). Polyester is exposed to Kyiv labor-starved lines (news_0011) and national logistics (news_0009) plus curfew/security rules at the Kyiv hub in `cotton-garment.md`. Mitigations: forward-contract cotton, shift mix toward polyester, and de-risk Kyiv dispatch windows.
- **Sources:** `data/products/cotton-garment.md`; `data/news/news-0009`, `news-0011`, `news-0020`

---

## Suggested evaluation order

1. Run the **Scenario 1** queries to verify Agent 1 graph retrieval returns the right entities/stages.
2. Run **Scenario 2** to verify Agent 2 joins by exact entity spelling and ranks by recency.
3. Run **Scenario 3** to verify the entity join between product and news collections works (especially the `Copper` hub cross-product case and the `Nickel` exception case).
4. Run **Scenario 4** to verify Agent 3 reason-from-supplied-facts behavior.
5. Run **Scenario 5** to verify full multi-agent orchestration, report saving, and presentation.

**Tip:** Entity spelling is a controlled vocabulary (see `DATA_PROMPT.md` §9). Queries phrased with the exact material names above (e.g. `Copper`, `Nickel`, `Silicon`, `Neodymium`) are the ones that will join cleanly.
