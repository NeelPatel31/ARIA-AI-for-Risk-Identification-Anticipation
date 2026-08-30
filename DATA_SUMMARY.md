# DATA_SUMMARY — ARIA Supply-Chain Risk Dataset (fast lookup)

Closed-system fake dataset. 8 products, 15 raw materials, 2 countries (+1 Nickel exception in Indonesia), 8 cities, 21 news events.

## 1. Products ↔ materials ↔ sites

| # | Product | Demand | Materials (stock/export) | Plant (city) + Hub | Hubs' materials |
|---|---------|--------|--------------------------|--------------------|-----------------|
| EV Vehicle | Moderate (Q4) | Battery[Li,Co,Gr](Med); Nickel alt (Limited/**Restricted**, ID); Steel(High) | Shenzhen Plant→Battery; Lviv Plant→Steel | SZ hub: Battery; Lviv hub: Steel |
| Smartphone | High | Battery[Li,Co,Gr](Med); Sulfuric Acid(High); Silicon(Low/**Controlled**); Copper(Med) | Suzhou Plant→Battery,SA; Nanjing Plant→Si,Cu | Suzhou hub: Battery,SA; Nanjing hub: Si,Cu |
| Solar Panel | High | Silicon(Low/**Controlled**); Copper(Med); Aluminum(Med); Zinc(Med) | Guangzhou Plant→Si,Cu; Bila Tserkva Plant→Al,Zn | GZ hub: Si,Cu; BT hub: Al,Zn |
| Bicycle | Moderate | Steel(High); Iron(High); Aluminum(Med); Titanium(Low/**Controlled**) | Guangzhou Plant→Al,Ti frames; Stryi Plant→Steel,Fe | GZ hub: Al,Ti; Stryi hub: Steel,Fe |
| Cotton Garment | Moderate | Cotton(Med); Polyester(Med) | Nanjing Plant→Cotton; Kyiv Plant→Polyester | Nanjing hub: Cotton; Kyiv hub: Polyester |
| Laptop | High | Battery[Li](Med); Silicon(Low/**Controlled**); Copper(Med); Aluminum(Med); Titanium(Low/**Controlled**) | Suzhou Plant→Battery,Si; Shenzhen Plant→Cu,Al,Ti chassis | Suzhou hub: Battery,Si; SZ hub: chassis |
| Wind Turbine | High | Steel(High); Copper(Med); Zinc(Med); Neodymium(Low/**Controlled**) | Lviv Plant→Steel; Nanjing Plant→Cu,Zn,Nd | Lviv hub: Steel; Nanjing hub: Cu,Zn,Nd |
| Steel Furniture | Low | Steel(High); Iron(High); Zinc(Med) | Guangzhou Plant→Zn; Bila Tserkva Plant→Steel,Fe | GZ hub: Zn; BT hub: Steel,Fe |

## 2. Raw materials (15)

| Material | Composition | Products (n) | Source | Price | Stock | Export status |
|----------|-------------|--------------|--------|-------|-------|---------------|
| Steel | Iron | EV, Bicycle, Wind Turbine, SteelFurniture (4) | China; Ukraine | 90–110 USD/tonne | High | Regular |
| Copper | Copper | Smartphone, Solar, WindTurbine, Laptop (4, hub) | China; Ukraine | 12 USD/unit | Medium | Regular |
| Aluminum | Aluminum | Solar, Bicycle, Laptop | China; Ukraine | 16–18 USD/unit | Medium | Regular |
| Lithium | — | EV, Smartphone, Laptop (battery) | China; Ukraine | n/a (component) | Medium | Regular |
| Cobalt | — | EV, Smartphone (battery) | China; Ukraine | n/a (component) | Medium | Regular |
| Graphite | — | EV, Smartphone (battery) | China; Ukraine | n/a (component) | Medium | Regular |
| Silicon | Silicon | Smartphone, Solar, Laptop | China (Suzhou/Nanjing/GZ) | 30–45 USD/unit | **Low** | **Controlled** |
| Titanium | Titanium | Bicycle, Laptop | China (GZ/Shenzhen) | 55–58 USD/unit | **Low** | **Controlled** |
| Neodymium | Neodymium | Wind Turbine | China (Nanjing) | 65,000 USD/tonne | **Low** | **Controlled** |
| Nickel | Nickel | EV (battery alt) | **Sulawesi, Indonesia** (sole source, outside closed set) | 18,500 USD/tonne | **Limited** | **Restricted** |
| Zinc | Zinc | Solar, WindTurbine, SteelFurniture | China; Ukraine (BT) | 20–22 USD/unit | Medium | Regular |
| Iron | Iron | Bicycle, SteelFurniture | Ukraine | 58–60 USD/tonne | High | Regular |
| Sulfuric Acid | Sulfuric Acid | Smartphone | China (Suzhou) | 8 USD/unit | High | Regular |
| Cotton | Cotton | Cotton Garment | China (Nanjing) | 3 USD/unit | Medium | Regular |
| Polyester | Polyester | Cotton Garment | Ukraine (Kyiv) | 2 USD/unit | Medium | Regular |

Hub/risk notes: **Steel & Copper = hub materials (4 products each)** — cross-product concentration risk. Cotton/Polyester/Neodymium = deliberate single-product nodes. Titanium is the only material used in 2 products but always **Low stock + Controlled**.

## 3. Locations → plants & hubs (plant capacity / hub cost)

**China**
- **Shenzhen, Guangdong**: Laptop Plant→Cu/Al/Ti chassis (100k u/m, $6); EV Plant→Battery (50k u/m, $15); SZ hub Laptop ($3.7k) + EV ($5k). Local rules: carbon-trading output cap + overtime limits (plants); fire-zone zoning, hazmat inventory cap (hubs).
- **Guangzhou, Guangdong**: Bicycle Plant→Al/Ti frames (25k u/m, $9); Solar Plant→Si/Cu (60k u/m, $6); SteelFurniture Plant→Zn (40k u/m, $8); hubs Bicycle ($2.8k), Solar ($3.5k), SteelFurniture ($3k). Rules: **Guangdong dual-control energy cap → mandatory curtailment** (plants); low-emission-zone/Euro VI truck windows (hubs).
- **Suzhou, Jiangsu**: Smartphone Plant→Battery+SA (200k u/m, $3); Laptop Plant→Battery+Si (120k u/m, $5); hubs $4.2k / $4k. Rules: water-pollution effluent quota + overtime caps (plants); bridge axle-weight limits + night-loading ban 22:00–06:00 (hubs).
- **Nanjing, Jiangsu**: Smartphone Plant→Si/Cu (180k u/m, $4); WindTurbine Plant→Cu/Zn/Nd (600 u/m, $25); CottonGarment Plant→Cotton (500k u/m, $1); hubs $3.8k / $5.5k / $2.2k. Rules: certified-recycling + escalating landfill fees (plants); reverse-logistics take-back (hubs).

**Ukraine**
- **Lviv, Lviv Oblast**: EV Plant→Steel (30k t/m, $10); WindTurbine Plant→Steel (5k t/m, $15); hubs $3k / $6k. Rules: martial-law + Ukrzaliznytsia rail slots + grid-rationing windows (plants); transit-terminal security passes + rail-slot windows (hubs).
- **Stryi, Lviv Oblast**: Bicycle Plant→Steel/Fe (15k t/m, $7); hub $2.1k. Rules: civil-defense air-raid shelters/firebreaks (plant); fire-buffer zoning + wartime roadblock clearances (hub).
- **Kyiv, Kyiv Oblast**: CottonGarment Plant→Polyester (300k u/m, $1); hub $1.9k. Rules: mobilization deferral paperwork + energy-rationing windows (plant); curfew halts departures + 24h convoy clearance + fuel reserves (hub).
- **Bila Tserkva, Kyiv Oblast**: Solar Plant→Al/Zn (40k u/m, $7); SteelFurniture Plant→Steel/Fe (20k t/m, $6); hubs $2.9k / $2.4k. Rules: mandatory stoppage on air-quality breach + emission permits (plants); mobile air monitoring + night noise rules (hub).

**Indonesia (exception, Nickel only)**: Sulawesi — sole Nickel source, Restricted export (domestic-processing mandate) + Limited stock.

Sourcing-only country notes: Copper/Cobalt/Graphite/Lithium source from "China; Ukraine" country-wide (no specific production site). Iron = Ukraine country-wide.

## 4. News events (21) — join via exact entity strings

| ID | Date | Type | Location | Material(s) | Summary / Impact |
|----|------|------|----------|-------------|------------------|
| 0001 | 08-04 | Price | Global (smelter cuts Chile/Asia) | Copper | +7% LME, global smelter cap −8%. **Mod-High** (hits SP, WindTurbine, Laptop, Smartphone) |
| 0002 | 08-10 | War | Ukraine (nationwide) | Steel, Battery comps | Op "Steel Corridor", 5–10 day delays, rail −30%. **High** |
| 0003 | 08-05 | Calamity | Shenzhen Longgang | Battery | Flood, 3–5 day shutdown, localized. **Moderate** |
| 0004 | 08-18 | Policy | Sulawesi, Indonesia | Nickel | Domestic-processing mandate expands. **High** (reinforces Restricted) |
| 0005 | 08-22 | Labor | Suzhou | Copper | Wire strike −20% regional output, 1–2 wks. **Moderate** |
| 0006 | 07-14 | Calamity | Guangzhou Panyu | Al, Zn, Si, Cu, Ti | Pearl R. flood, 4–7 day shutdown, rail +2d via Dongguan. **Mod-High** (broad because co-located) |
| 0007 | 07-21 | Calamity | Stryi | Steel, Iron | Wildfire shutdown 3–5 d, Fe ore held at siding; Lviv unaffected. **Moderate** |
| 0008 | 07-28 | Calamity | Sulawesi | Nickel | Landslide buries haul road, 10–14 d; 2 wks buffer. **High** |
| 0009 | 08-02 | War | Ukraine (nationwide) | Steel, Polyester | Black Sea drone strikes, Op "Coastal Shield", +6–9 d, ports suspended. **High** |
| 0010 | 08-09 | War | Ukraine (nationwide) | Cu, Zn, Al | Rail bridge strikes, freight weight cap 60%, week+ delays. **High** |
| 0011 | 08-13 | War | Ukraine (nationwide) | Steel, Iron, Polyester | Mobilization −8% factory workforce, line staff −⅓. **Mod-High** (labor) |
| 0012 | 07-17 | Policy | China (nationwide) | Graphite | Export licenses w/ end-use declaration, +2–3 wks. **High** |
| 0013 | 07-24 | Policy | Guangdong | Aluminum | Dual-control energy −15%, up to 20% curtailment by Sep, −60kt. **Moderate** |
| 0014 | 08-06 | Policy | Ukraine (nationwide) | Zinc | 70% export quota, allocation certificates. **Mod-High** |
| 0015 | 07-30 | Labor | Nanjing | Cu, Zn, Neodymium | ~400 workers strike; Nd line hit hardest, Cu at 60%. **Moderate** |
| 0016 | 08-11 | Labor | Bila Tserkva | Al, Zn | Safety/ventilation stoppage, 150 workers, reopen ≤48h. **Low-Mod** |
| 0017 | 08-16 | Labor | Shenzhen | Ti, Cu, Al | Contract slowdown → chassis ~½ capacity, ~1 wk delay. **Low-Mod** |
| 0018 | 08-19 | Price | Global (Indonesia orig.) | Nickel | LME +9%, battery-grade nickel sulfate premium widens; LME stock 14-mo low. **High** |
| 0019 | 08-24 | Price | Global (demand, China/Ukraine orig.) | Lithium | Carbonate +11% futures, demand-side. **Mod-High** |
| 0020 | 08-27 | Price | Global (China orig.) | Cotton | +8% futures, crop downgrades; pushes Polyester substitution. **Moderate** |
| 0021 | 08-29 | Price | Brazil (Minas Gerais) | Coffee Beans | **Out-of-scope decoy** — Coffee/Brazil not in closed set, joins to no product. |

Event-type mix: 4 Natural Calamity, 4 War/Conflict, 4 Government Policy, 4 Labor Dispute, 4 Economic/Price Shock, 1 deliberate out-of-scope (0021).

Cluster theme: Ukraine logistics is degraded on all fronts (war, rail, labor, ports, zinc quota) — every Ukraine-sourced material carries elevated risk. China risk is more local (city/event-specific) except Graphite export licensing (nationwide).

## 5. Agents & retrieval flow

- **Coordinator** (agent.py) orchestrates subagents; reports saved as named state: `product_dossier` → `news_brief` → `risk_assessment` → `mitigation_plan` (tools: save/read/present_report, write/read_todos).
- **product_cartographer**: product/supply-chain context via `knowledge_search` (GraphRetriever, Eager: select_k=9, start_k=4, max_depth=4) over product collection.
- **disruption_scout**: compiles news via `news_search` (news collection) + read_report; news sorted by published_date desc (recency).
- **mitigation_strategist**: traces scored risks to root cause + cites mitigations.
- **Risk scoring (deterministic)**: per-risk = round(S×E×F/12.5), clamp 1–10; cumulative = RMS of all scores, clamp 1–10. Bands: 1–3 Low, 4–6 Moderate, 7–8 High, 9–10 Critical. Derived from Sourcing/Manufacturing/Delivery evidence, never guessed.
- **Join rule**: news links to products only when closed-set entity spellings intersect (exact string match). A typo silently breaks retrieval.

## 6. Key risk hotspots (built into the data)

1. **Guangzhou** — 3 products share one city's energy cap + flood exposure; 0006 flood hit 5 materials.
2. **Shenzhen** — 2 products, carbon cap + flood + labor slowdown (0017).
3. **Nickel (Sulawesi)** — sole-source outside safe zone: Restricted export + Limited stock + policy (0004) + calamity (0008) + price surge (0018).
4. **Titanium / Silicon / Neodymium** — Low stock + Controlled export, single-country (China) source.
5. **Ukraine-wide** — war logistics (rail −40% capacity) + mobilization labor + zinc quota + port suspension.
6. **Copper** — hub material (4 products), price shock (0001) + Suzhou strike (0005) + Ukraine rail (0010).