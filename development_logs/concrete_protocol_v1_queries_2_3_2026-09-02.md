# Concrete protocol version — Queries 2 and 3 live comparison

- Generated: 2026-09-02T19:24:56.382621+00:00
- Mode: `live — concrete_protocol_v1`
- Model: `gpt-5.4-mini`
- Query count: 2
- Source queries: Queries 2 and 3 of the original five-query evaluation
- Prompt/output version: `concrete_protocol_v1`
- Purpose: diagnose retrieval relevance, protocol specificity, analogue transfer, and appropriate refusal.

The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.

## Query 2: Concrete protocol version — Specific NMC811 pouch-cell target

### Exact query

> Propose an evidence-supported starting fast-charge protocol for a 5 Ah graphite/NMC811 pouch cell at 25 °C, charging from 10% to 80% SOC with a target time of 20 minutes while limiting lithium plating. Give current stages and transition criteria only when supported, and clearly identify values that cannot be determined from the evidence.

### Intended test

Concrete protocol version: whether detailed target conditions produce an ordered, experimentally actionable candidate protocol while clearly distinguishing reported, extrapolated, and unresolved values.

### Supplied operating conditions

- chemistry: graphite/NMC811
- form_factor: 5 Ah pouch cell
- temperature: 25 °C
- soc_range: 10-80%
- objective: target 20 minutes while limiting lithium plating

### Execution and validation

- Validation: `pass_with_warnings`
- Warnings: 2
- Agent rounds: 3
- Tool calls: 6
- JSON repair attempts: 0
- Input tokens: 6856
- Output tokens: 3289
- Total tokens: 10145
- Elapsed seconds: 104.21
- Retrieved chunks retained: 9
- Distinct papers retained: 4

#### Validation warnings

- protocol_suggestions[1] contains numerical values not found verbatim in cited evidence: 20 min, 6C, 30 A, 15 A, 1C, 5 A; disclosed as extrapolation
- protocol_suggestions[2] contains numerical values not found verbatim in cited evidence: 25 °C, 4C, 25 A, 25 °C, 25 °C, 25 °C; disclosed as extrapolation

### Generated answer

The evidence base is only partially matched to the requested graphite/NMC811, 5 Ah pouch cell at 25 °C. The strongest directly relevant findings are: (1) fast-charge protocols for graphite/NMC cells should reduce current as voltage rises to limit lithium plating; (2) for a modeled graphite/NMC532 cell, a 5C+CC stage should be terminated below 4.1 V to avoid plating, and multi-stage CC can reduce plating driving force relative to CCCV at very high initial rates; (3) a validated experimental fast-charge protocol on a constrained pouch cell at 25 °C achieved 0–85% SOC in 26.8 min with no abnormal capacity loss over 100 cycles, but the chemistry is not specified as NMC811 and the exact current steps are not in the retrieved chunk. Because no exact-match NMC811/5 Ah/25 °C/10–80%/20 min protocol was found, the suggestions below are conservative starting points synthesized or extrapolated from these sources and should be experimentally validated with cell-specific voltage, temperature, and plating diagnostics.

#### Protocol suggestions

**1. Conservative multi-stage CC with early taper; start from a high initial current and reduce current before high-voltage region to limit plating risk**

- Origin: `synthesized`
- Confidence: `low`
- Rationale: This protocol is a conservative synthesis of the retrieved evidence. The model study reports that higher current should be used when voltage is low and lower current when voltage is high to avoid lithium plating, and that multi-stage CC can reduce plating driving force compared with CCCV at very high initial rates. The same study also indicates that for a graphite/NMC532 cell, a 5C+CC stage should be terminated below 4.1 V to prevent plating. The experimental constrained-pouch-cell study at 25 °C shows that a fast-charge protocol can reach 85% SOC in 26.8 min without abnormal capacity loss over 100 cycles, supporting the feasibility of a fast-charge starting point at this temperature, though the exact current profile is not available in the retrieved chunk. Because the requested chemistry is NMC811 rather than NMC532 and the cell is 5 Ah rather than the smaller modeled cell, the current values here are provisional starting values rather than directly reported settings.
- Applicable conditions: graphite/NMC pouch cell; 25 °C cell temperature; 10% to 80% SOC target window; 5 Ah class cell; objective is to approach 20 min while limiting lithium plating
- Extrapolation used: True
- Limitations: No directly retrieved protocol matches graphite/NMC811, 5 Ah, 25 °C, and 10% to 80% SOC exactly.; The exact current steps and voltage transitions for the 25 °C experimental fast-charge protocol were not available in the retrieved chunk.; The 4.1 V transition concept comes from a modeled graphite/NMC532 cell and may not transfer directly to NMC811 without adjustment.; The proposed current values are extrapolated starting points, not reported values.; Lithium plating detection method is not specified in the evidence and must be chosen experimentally.
- Evidence chunks: `unknown_2020::chunk::0066`, `unknown_2020::chunk::0028`, `unknown_2020::chunk::0067`, `doi_10.1149_1945-7111::chunk::0049`

##### Candidate protocol steps

**Stage 1: Stage 1: high-current CC**

- Current/C-rate: Start at a provisional 5C to 6C (25–30 A for a 5 Ah cell)
- Start: Begin at 10% SOC and 25 °C cell temperature
- Transition: Transition when cell voltage approaches the conservative upper-voltage region; exact threshold unresolved from evidence, but use a cell-specific limit below the manufacturer maximum and consider an initial trial cutoff near 4.1 V as a conservative starting point
- Temperature constraints: Hold near 25 °C; do not allow cell temperature to rise beyond manufacturer limit; If temperature rises materially above the test condition, reduce current or stop
- Monitoring: Cell voltage; Cell temperature; Charge current; Optional plating-sensitive diagnostics such as dV/dt, incremental capacity, or reference-electrode/impedance methods if available
- Stop conditions: Any cell voltage limit from manufacturer or test plan is reached; Temperature limit reached; Evidence of lithium plating or abnormal polarization is detected; Safety system flags abnormal pressure/temperature rise
- Value basis: `extrapolated`

**Stage 2: Stage 2: reduced-current CC**

- Current/C-rate: Reduce to a provisional 2C to 3C (10–15 A)
- Start: Enter when the voltage transition criterion from Stage 1 is met
- Transition: Continue until the cell nears the upper SOC region where plating risk increases; exact SOC/voltage boundary unresolved from evidence
- Temperature constraints: Maintain near 25 °C; Avoid sustained temperature rise relative to the baseline test condition
- Monitoring: Cell voltage; Cell temperature; Current acceptance; Signs of increasing overpotential
- Stop conditions: Voltage limit reached; Temperature limit reached; Plating indicators appear
- Value basis: `extrapolated`

**Stage 3: Stage 3: low-current finish or CV hold**

- Current/C-rate: Either a low-current CC tail at about C/2 to 1C (2.5–5 A) or a brief CV hold at the manufacturer-approved upper voltage; exact choice unresolved
- Start: Begin when the cell enters the final approach to 80% SOC or the upper-voltage region
- Transition: Terminate at 80% SOC or when current tapers to a low threshold set by the test plan; exact current cutoff unresolved
- Temperature constraints: Maintain near 25 °C; Do not exceed manufacturer thermal limits
- Monitoring: Cell voltage; Taper current; Cell temperature; Post-charge relaxation response if used
- Stop conditions: 80% SOC reached; Voltage limit reached; Current taper criterion reached; Any plating or safety concern
- Value basis: `unresolved`

##### Extrapolation disclosure

- Justification: The retrieved evidence supports the qualitative control principle that current should be reduced as voltage rises to limit plating, and it provides a conservative voltage-cutoff concept near 4.1 V for a graphite/NMC cell under fast charge. The 25 °C experimental study supports that fast charging at this temperature can be feasible without obvious degradation, but it does not specify NMC811 or the exact current schedule. Therefore, the proposed currents are deliberately provisional starting values chosen to be aggressive enough to approach the 20 min target while remaining below the most extreme rates discussed in the evidence.
- Source conditions: graphite/NMC532 modeled cell at moderate loading; single-layer or constrained pouch-cell fast-charge studies; 25 °C experimental constrained cell; voltage cutoff guidance around 4.1 V in modeled graphite/NMC532 cell
- Target conditions: graphite/NMC811; 5 Ah pouch cell; 25 °C; 10% to 80% SOC; target 20 min
- Key differences: Cathode chemistry differs (NMC811 vs NMC532 or unspecified NMC); Cell capacity differs (5 Ah vs smaller modeled or unspecified cells); Exact electrode loading, N:P ratio, and voltage window are unknown; No direct evidence for 10% to 80% SOC in 20 min at 25 °C for this exact cell

##### Validation plan

- First screen the protocol on a small number of cells with conservative current ceilings and a hard voltage limit set by the manufacturer.
- Instrument at least voltage and temperature; if possible add reference-electrode, impedance, or post-charge relaxation diagnostics to detect lithium plating.
- Compare several variants around the provisional current levels (for example, 4C/2C/1C, 5C/3C/1C, 6C/3C/1C) to find the fastest profile that does not show plating signatures.
- Use short cycle blocks with capacity checks and post-charge relaxation to look for abnormal voltage shoulders or capacity loss.
- If plating indicators appear, reduce the first-stage current and/or lower the transition voltage before increasing charge aggressiveness.
- Do not treat the provisional 4.1 V concept as universal; re-optimize for the specific NMC811 cell and its manufacturer limits.

**2. CC-to-CV style fast charge with an early conservative voltage cutoff; use only if the cell’s manufacturer allows a CV phase and if plating diagnostics are available**

- Origin: `synthesized`
- Confidence: `low`
- Rationale: The evidence indicates that CCCV can be outperformed by multi-stage CC in terms of plating driving force at very high initial rates, but CCCV remains a common baseline and the retrieved model study explicitly discusses CCCV/CPCV screening. This makes a conservative CC-to-CV profile a reasonable comparator for experimental screening, especially if the goal is to benchmark against a simpler protocol. The voltage cutoff should be conservative because the model study warns that a 5C+CC stage should end below 4.1 V to prevent plating in a graphite/NMC532 cell. However, because the evidence also suggests that multi-stage CC may be better than CCCV at extreme rates, this protocol should be treated as a baseline rather than the preferred final design.
- Applicable conditions: graphite/NMC pouch cell; 25 °C; 5 Ah class; 10% to 80% SOC; research screening where a CV tail is acceptable
- Extrapolation used: True
- Limitations: The evidence suggests CCCV may be inferior to multi-stage CC at very high rates for plating control.; No exact CV cutoff current is supported by the retrieved evidence.; No direct NMC811-specific validation is available.
- Evidence chunks: `unknown_2020::chunk::0022`, `unknown_2020::chunk::0028`, `unknown_2020::chunk::0066`

##### Candidate protocol steps

**Stage 1: Stage 1: constant-current charge**

- Current/C-rate: Provisional 4C to 5C (20–25 A for a 5 Ah cell)
- Start: Start at 10% SOC and 25 °C
- Transition: Switch to CV when cell voltage reaches a conservative upper threshold; evidence supports using a threshold below 4.1 V as a starting point for a graphite/NMC cell, but the exact value for NMC811 is unresolved
- Temperature constraints: Maintain 25 °C nominally; Abort or reduce current if temperature rises beyond manufacturer limits
- Monitoring: Voltage; Temperature; Current; Optional plating diagnostics
- Stop conditions: Upper voltage limit reached; Temperature limit reached; Plating indicators appear
- Value basis: `extrapolated`

**Stage 2: Stage 2: constant-voltage hold**

- Current/C-rate: CV at the chosen upper-voltage limit; current tapers naturally
- Start: Enter at the Stage 1 voltage threshold
- Transition: End CV when current falls to a low cutoff chosen by the test plan or when 80% SOC is reached; exact cutoff unresolved
- Temperature constraints: Maintain near 25 °C; Do not exceed manufacturer thermal limits
- Monitoring: Taper current; Voltage; Temperature
- Stop conditions: 80% SOC reached; Current taper cutoff reached; Temperature or safety limit reached
- Value basis: `unresolved`

##### Extrapolation disclosure

- Justification: CCCV is a standard experimental baseline and the evidence provides a conservative voltage-cutoff concept plus a general warning that higher initial current increases plating risk. The exact current and cutoff for NMC811 are not directly reported, so the values are provisional.
- Source conditions: graphite/NMC532 model screening of CCCV/CPCV; 25 °C experimental fast-charge context
- Target conditions: graphite/NMC811; 5 Ah pouch cell; 10% to 80% SOC
- Key differences: NMC811 may have different voltage/polarization behavior than NMC532; 5 Ah cell may have different thermal response than the modeled or smaller cells; The evidence does not provide a validated CV termination current for this cell

##### Validation plan

- Use this only as a benchmark against the multi-stage CC protocol.
- Measure whether the CV tail materially increases time without reducing plating signatures.
- If plating is observed, lower the CC current or lower the CV entry voltage.
- Compare capacity retention and relaxation behavior against the multi-stage CC option.

#### Conflicting evidence

- The model study reports that CCCV/CPCV can outperform multi-stage CC in some regimes, but also states that at very high initial rates multi-stage CC can reduce the maximum plating driving force relative to CCCV/CPCV; this means the preferred structure depends on the exact rate regime and cell design.
- The 25 °C experimental constrained-cell study demonstrates a fast-charge protocol with good cycling stability, but the exact current schedule is not available in the retrieved chunk, so it cannot directly justify a specific current profile for NMC811.
- The only explicit voltage threshold retrieved is a modeled recommendation to terminate a 5C+CC stage below 4.1 V for a graphite/NMC532 cell; transfer to NMC811 is plausible but not directly supported.

#### Missing information

- Exact current steps and voltage transitions for a validated 25 °C fast-charge protocol
- NMC811-specific plating onset data for the exact 5 Ah pouch cell
- Manufacturer maximum charge voltage, thermal limits, and allowable CV termination current
- Electrode loading, N:P ratio, separator, electrolyte, and cell geometry
- Direct plating-detection method to use during protocol development
- Whether the cell can safely tolerate a CV phase or should remain CC-only

#### Safety notes

- Do not exceed the manufacturer’s voltage, current, or temperature limits.
- Use cell-specific instrumentation and stop immediately if temperature, pressure, or voltage behavior indicates abnormal polarization or possible plating.
- Treat all proposed currents and voltage thresholds as experimental starting points, not deployment-ready settings.
- Because the evidence is not NMC811-specific, begin with conservative currents and a lower voltage cutoff, then increase only after confirming no plating signatures.
- Do not rely on SOC alone; use voltage and temperature as primary real-time safeguards.

#### Follow-up questions

- What is the manufacturer’s maximum charge voltage and recommended charge current for this exact 5 Ah NMC811 pouch cell?
- Can the cell be instrumented with a reference electrode or another plating-sensitive diagnostic?
- What are the electrode areal loadings and N:P ratio?
- Is a CV phase permitted, or must the protocol remain CC-only?
- What plating criterion will be used to accept or reject a candidate protocol?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | [13] | 0.8786934018135071 | 0.772662716945294 | `unknown_2020::chunk::0067` |
| 2 | Extreme Fast Charge Challenges for Lithium-ion Battery: Variability and Positive Electrode Issues | Experimental | [5] | 0.875095784664154 | 0.7855472565894285 | `tanim_2015::chunk::0008` |
| 3 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | [13] | 0.8661078810691833 | 0.7909473915467107 | `unknown_2020::chunk::0066` |
| 4 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Discussion | [11] | 0.8621857762336731 | 0.7830585657724372 | `unknown_2020::chunk::0057` |
| 5 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Screening of Conventional Protocols Using the Pseudo2D Model | [5] | 0.8603463768959045 | 0.7971119392408116 | `unknown_2020::chunk::0022` |
| 6 | Investigation of Temperature and Pressure Behaviour of Constrained Lithium Ion Cell under Lithium Plating Conditions | Results and Discussion | [11] | 0.8933550119400024 | 0.7860342206387982 | `doi_10.1149_1945-7111::chunk::0049` |
| 7 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Screening of Conventional Protocols Using the Pseudo2D Model | [6] | 0.8865808248519897 | 0.7860154062043826 | `unknown_2020::chunk::0028` |
| 8 | Non-destructive fast charging algorithm of lithium-ion batteries based on the control-oriented electrochemical model | 4. Applying the fast charging algorithm to a commercial lithium-ion battery: experimental validation | [6, 7] | 0.8738889098167419 | 0.8059982232039277 | `pdf_e648a41cdcfc30f1::chunk::0032` |
| 9 | Investigation of Temperature and Pressure Behaviour of Constrained Lithium Ion Cell under Lithium Plating Conditions | Experimental | [3] | 0.8714893460273743 | 0.8081091472341074 | `doi_10.1149_1945-7111::chunk::0014` |

#### Evidence excerpts

**1. `unknown_2020::chunk::0067`**

achieve fast charging without lithium plating, the cell should be charged at a higher current when the cell voltage is low, and charged to higher voltage when the charge current is low. Conclusions Based on the features of the semi-optimal protocol, two practical novel fast charging protocols were proposed, namely the voltage ramping protocol and the multiple CCCV protocol. The simulation results showed that for the 2.5 mAh cm -2 cell, the maximum capacity after 10 min charge at 30 °C without lithium plating can be improved by up to 10.7% using the proposed protocols compared with the standard CCCV protocol. To achieve 80% charge in 10 min, the proposed protocols will require a charging t...

**2. `tanim_2015::chunk::0008`**

charging. These issues are often overlooked due to the focus on Li metal plating during fast charging, but have the potential to significantly impact the eventual application and use of fast charging. Experimental Table I lists the material, electrode, cell design parameters, and Table II includes the charging protocols. Graphite (1506T Superior Graphite) and NMC532 (Toda America) were used as respective negative and positive electrode active materials, respectively, to fabricate electrodes at the Cell Analysis, Modeling, and Prototyping (CAMP) Facility at Argonne National Laboratory (Argonne). These electrodes were cut and assembled in single layer pouch cells with Celgard 2320 separator...

**3. `unknown_2020::chunk::0066`**

ing protocol. However, several CCCV steps are likely needed as the higher loading cell is more prone to lithium plating, increasing implementation complexity compared to the voltage ramping protocol. Conclusions In this work, the Pseudo2D electrochemical battery model was used to screen traditional fast charging protocols for a moderate HEV loading (2.5 mAh cm -2 ) graphite/NMC 532 cell. The simulation results showed that in terms of the maximum driving force for lithium plating, CCCV and CPCV protocols outperform the multistage constant-current charging with a single voltage cutoff and the pulse charging. To prevent lithium plating, the 5C + constant-current charging stage should be term...

**4. `unknown_2020::chunk::0057`**

ating capacity can be further increased by using a higher initial C rate, it is likely to trigger degradation mechanisms other than lithium plating, such as cathode cracking and excessive heat generation. Discussion Achieve 80% charge in 10 min at elevated temperature. -Figure 8 shows that the investigated moderate loading cell can only be charged to SOC = 74.1% within 10 min even when the semioptimal protocol is used, when the ambient temperature is T 0 = 30 °C. To achieve the goal of charging 80% in 10 min, the proposed fast charging protocols need to be combined with other measures, such as using electrodes with advanced architecture or charging the cell at a higher temperature. The la...

**5. `unknown_2020::chunk::0022`**

-of-charge after 10 min charging using CCCV or CPCV protocol. The colorbar of the symbols re fl ect the mean cell temperature during the charging process. Screening of Conventional Protocols Using the Pseudo2D Model To investigate how the charge rate in fl uences the driving force of lithium plating, a parameter sweep is performed such that the investigated cell is charged with a wide range of n C CCCV and n P CPCV protocols, up to 10C and 10P, respectively. Figure 3 summarizes the simulation results, the x axis of which is the state-ofcharge (SOC = ò I t d /(35.25 mAh)) of the cell after 10 min charging while the y axis is the maximum driving force for lithium plating during the charging...

**6. `doi_10.1149_1945-7111::chunk::0049`**

the stepwise protocol is reduced to the next lower current before lithium deposition onset is reached. The resulting fast charging protocol based on onset of lithium deposition is shown in Table II. Results and Discussion The shown fast charge protocol allows a charging of the cell from 0%SoC to 85%SoC in 26.8 min. To validate the developed charging protocol three cells were cycled with this protocol. Start condition was 25 °C ±1 °C cell temperature and the temperature of the chamber held constant. Cells were cycled in the already presented test setup (refer to Fig. 1) to realize the same test conditions as in second test case. The cycling was started at 0%SoC and the cell was charged wit...

**7. `unknown_2020::chunk::0028`**

the C rate in the fi rst stage. Using constant-current steps with lower currents in following stages only reduces the charge acceptance but cannot change the maximum plating driving force. Screening of Conventional Protocols Using the Pseudo2D Model As a result, at given min( f f -s e ) (determined by C rate in the fi rst stage), the cell SOC after 10 min charge with the multi-stage constant-current protocol is smaller than those with CCCV and CPCV, independent of how many CC steps are used as long as the cutoff voltage is fi xed at 4.1 V. Note that a few data points of the multi-stage protocol show lower driving force of lithium plating than CCCV, when the charge acceptance in 10 min is ...

**8. `pdf_e648a41cdcfc30f1::chunk::0032`**

Fig. 5. Profiles of charging from different initial OCV: (a)-(c) 3.73 V, (d)-(f) 3.86 V. 4. Applying the fast charging algorithm to a commercial lithium-ion battery: experimental validation The test results obtained by applying the fast charging algorithm to a large-format commercial lithium-ion battery with an incorporated reference electrode are presented in this section. The commercial pouch cells consisted of NCM/graphite electrodes. The nominal capacity was 40 A h, and the voltage range was 2.84.2 V. To construct a three-electrode cell, the oxidation was removed from a 25l m-diameter copper wire by acid washing, and the wire was then placed on the surface of the anode/separator inter...

**9. `doi_10.1149_1945-7111::chunk::0014`**

phase lithium plating conditions should be achieved. After CC-charge phase a relaxation phase of 2 h has been allowed followed by 1/3 C discharge to 0% SoC. Experimental After each CC-charge test and following discharge a capacity check has been performed. In this check the cell was fully charged with 1/3 C followed by a constant voltage (short: CV) phase and after a suf fi cient relaxation time also discharged with 1/3 C to 0%SoC without CV phase. For all tested conditions in the test case two, new cells were used to eliminate the in fl uence of cell ageing due to lithium plating condition in the test before. Figure 1. Test setup layout for constrained li-ion cell measurement. The third ...

---

## Query 3: Concrete protocol version — Known NCM523 evidence target

### Exact query

> Using retrieved experimental evidence, describe a starting fast-charge protocol design for an NCM523/graphite laboratory cell at 30 °C over 0-80% SOC that is intended to avoid lithium plating. Distinguish directly reported protocol elements from synthesis and inference.

### Intended test

Concrete protocol version: whether retrieval recovers the known Part V protocol paper and whether the answer converts that evidence into concrete stages with transparent extrapolation and validation requirements.

### Supplied operating conditions

- chemistry: NCM523/graphite
- form_factor: laboratory cell
- temperature: 30 °C
- soc_range: 0-80%
- objective: avoid lithium plating

### Execution and validation

- Validation: `pass_with_warnings`
- Warnings: 1
- Agent rounds: 4
- Tool calls: 7
- JSON repair attempts: 1
- Input tokens: 20749
- Output tokens: 6064
- Total tokens: 26813
- Elapsed seconds: 97.54
- Retrieved chunks retained: 16
- Distinct papers retained: 7

#### Validation warnings

- protocol_suggestions[1] contains numerical values not found verbatim in cited evidence: 0 V; disclosed as extrapolation

### Generated answer

Experimental evidence for NCM523/graphite laboratory cells at 30 °C supports anode-potential-aware fast charging to 80% SOC as the safest starting point for avoiding lithium plating. Directly reported elements include an initial 6C fast-charge segment, no-rest seesaw charging, and an anode-potential-controlled protocol targeting about −25 mV vs Li/Li+ with average rates around 4.9–5.1C to 80% SOC. A related study reports 4.97C average charge to 80% SOC for a 70 μm graphite electrode and 7.40C for a 47 μm electrode at 30 °C. Safe-line work further supports using anode-potential limits rather than fixed current alone, but the exact safe-line values are model-derived. The most defensible starting design is therefore a conservative variable-current protocol with continuous anode-potential monitoring, a 6C ceiling only as an initial starting point, and tapering whenever the anode potential approaches the plating boundary.

#### Protocol suggestions

**1. Conservative anode-potential-controlled variable-current charge**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: This is the most conservative synthesis of the directly reported NCM523/graphite evidence. The literature reports a 6C starting point, no-rest seesaw charging, and an anode-potential-controlled protocol with a target around −25 mV that avoided Li plating at 30 °C. It also reports average rates near 4.97C to 80% SOC for a 70 μm graphite electrode and 7.40C for a thinner 47 μm electrode. Because the user asked for a starting protocol intended to avoid plating, the protocol keeps the reported 6C only as an initial ceiling and relies on measured anode potential for tapering.
- Applicable conditions: NCM523/graphite laboratory cell; 30 °C; 0-80% SOC; three-electrode or equivalent anode-potential monitoring available; objective: avoid lithium plating
- Extrapolation used: True
- Limitations: The exact taper schedule is not directly reported for this specific cell.; Transferability depends on electrode thickness, loading, electrolyte, and reference-electrode placement.; Without anode-potential measurement, plating avoidance cannot be assured.
- Evidence chunks: `pdf_6fec389acaf110ab::chunk::0004`, `pdf_6fec389acaf110ab::chunk::0032`, `pdf_6fec389acaf110ab::chunk::0031`, `pdf_6fec389acaf110ab::chunk::0033`, `soc_2020::chunk::0044`, `soc_2020::chunk::0043`

##### Candidate protocol steps

**Stage 1: Initial fast-charge segment**

- Current/C-rate: Start at up to 6C
- Start: Begin at low SOC with cell temperature stabilized at 30 °C and within manufacturer voltage limits
- Transition: Reduce current when anode reference potential approaches a conservative negative threshold near −25 mV vs Li/Li+ or when polarization increases
- Temperature constraints: Hold near 30 °C; reduce current if temperature rises
- Monitoring: Anode reference potential; Cell voltage; Cell temperature; SOC
- Stop conditions: Anode potential approaches 0 V vs Li/Li+; Manufacturer voltage limit reached; Temperature limit reached; 80% SOC reached
- Value basis: `reported`

**Stage 2: Tapered continuation**

- Current/C-rate: Step down below 6C as needed to preserve plating margin
- Start: Triggered by shrinking anode-potential margin
- Transition: Continue lowering current whenever the anode potential nears the conservative threshold
- Temperature constraints: Maintain 30 °C
- Monitoring: Anode reference potential; Cell voltage; Cell temperature; SOC
- Stop conditions: Cannot maintain safe anode potential without further taper; 80% SOC reached
- Value basis: `extrapolated`

**Stage 3: Finish to 80% SOC**

- Current/C-rate: Use the lowest current that keeps the anode safely above the plating boundary
- Start: Late-stage charge when polarization is highest
- Transition: Terminate at 80% SOC
- Temperature constraints: Maintain 30 °C
- Monitoring: Anode reference potential; Cell voltage; Cell temperature; SOC
- Stop conditions: 80% SOC reached; Any safety limit reached
- Value basis: `extrapolated`

##### Extrapolation disclosure

- Justification: The chemistry, temperature, and endpoint match the user’s case, but the exact cell geometry and electrode thickness may differ. Therefore the protocol is adapted conservatively from the reported control concept rather than copied as a fixed schedule.
- Source conditions: NCM523/graphite laboratory cells at 30 °C; Charge to 80% SOC; Reported 6C initial segment and anode-potential-controlled operation
- Target conditions: User-specified NCM523/graphite laboratory cell at 30 °C over 0-80% SOC
- Key differences: Exact electrode thickness/loading may differ; Exact current waveform is not fully specified in the retrieved excerpt; The −25 mV target should be treated as a starting value, not a universal limit

##### Validation plan

- Measure anode potential in the actual laboratory cell before increasing aggressiveness.
- Pilot around the reported 6C starting point and lower currents to identify the highest plating-safe current.
- Confirm absence of plating with post-charge diagnostics before adopting the protocol as a routine starting condition.

**2. Reported seesaw charging with no rests**

- Origin: `reported`
- Confidence: `medium`
- Rationale: The experimental paper explicitly reports seesaw charging at 30 °C for NCM523/graphite cells, starting from I0 = 6C and charging to 80% SOC with no rests. It was presented as a plating-avoidance approach using anode-potential monitoring. This is the most directly reported protocol concept available for the user’s conditions.
- Applicable conditions: NCM523/graphite laboratory cell; 30 °C; 0-80% SOC; three-electrode monitoring available
- Extrapolation used: False
- Limitations: The retrieved excerpt does not expose the full step-by-step seesaw schedule.; Requires reference-electrode instrumentation and control logic.; May not transfer directly to a different laboratory cell geometry.
- Evidence chunks: `pdf_6fec389acaf110ab::chunk::0032`, `pdf_6fec389acaf110ab::chunk::0031`, `pdf_6fec389acaf110ab::chunk::0033`, `pdf_6fec389acaf110ab::chunk::0004`

##### Candidate protocol steps

**Stage 1: Seesaw fast-charge start**

- Current/C-rate: 6C initial current
- Start: Begin charge at 30 °C from low SOC
- Transition: Switch current according to the seesaw control law when the anode reference potential approaches the plating boundary
- Temperature constraints: Maintain 30 °C
- Monitoring: Anode reference potential; Cell voltage; SOC; Temperature
- Stop conditions: Anode potential approaches or crosses the plating boundary; Voltage or temperature limit reached; 80% SOC reached
- Value basis: `reported`

**Stage 2: Seesaw continuation**

- Current/C-rate: Variable stepwise current; no rests between steps
- Start: After the initial 6C segment
- Transition: Continue stepwise current changes until 80% SOC
- Temperature constraints: Maintain 30 °C
- Monitoring: Anode reference potential; Cell voltage; SOC; Temperature
- Stop conditions: 80% SOC reached; Any safety limit reached
- Value basis: `reported`

##### Validation plan

- Use only if the laboratory setup can measure anode reference potential reliably.
- Verify that the anode potential remains above the plating threshold under the local cell configuration.
- Check post-charge diagnostics for plating before increasing current aggressiveness.

**3. Reference-electrode-guided potentiostatic target around −25 mV**

- Origin: `reported`
- Confidence: `medium`
- Rationale: The cited paper reports a potentiostatic/anode-potential-control condition with a target of about −25 mV and an estimated average current of 4.88C, compared with 5.07C for the optimal zero-anode-potential control. It also reports the 30 °C experiments using an initial 6C charge to 80% SOC. This makes an anode-potential-target protocol a strong starting candidate for plating avoidance in the user’s cell.
- Applicable conditions: NCM523/graphite laboratory cell; 30 °C; 0-80% SOC; three-electrode monitoring available
- Extrapolation used: False
- Limitations: The exact current trajectory is not fully specified in the retrieved excerpt.; The −25 mV target is not a universal limit.; Transferability depends on cell-specific polarization and reference-electrode placement.
- Evidence chunks: `pdf_6fec389acaf110ab::chunk::0032`, `pdf_6fec389acaf110ab::chunk::0031`, `pdf_6fec389acaf110ab::chunk::0033`, `pdf_6fec389acaf110ab::chunk::0004`

##### Candidate protocol steps

**Stage 1: Anode-potential-targeted fast charge**

- Current/C-rate: Adjust current to keep anode reference potential near about −25 mV vs Li/Li+
- Start: Begin from low SOC at 30 °C with an initial fast-charge current consistent with the reported 6C starting point
- Transition: Modify current whenever the anode potential drifts outside the target band or toward the plating boundary
- Temperature constraints: Maintain 30 °C
- Monitoring: Anode reference potential; Cell voltage; SOC; Temperature
- Stop conditions: 80% SOC reached; Anode potential cannot be held near the target without violating voltage or temperature limits; Any sign of plating
- Value basis: `reported`

##### Validation plan

- Implement only in a three-electrode test cell or equivalent setup that can measure anode potential.
- Check whether the cell can hold the anode potential near the reported target without excessive voltage rise.
- Use post-charge diagnostics to confirm no plating before routine use.

#### Conflicting evidence

- At 30 °C, the safe-line paper indicates that higher temperatures improve safe charge capability relative to 30 °C, but it also warns that gains above 45 °C can be offset by resistance growth and long-term degradation; this supports 30 °C as a reasonable operating point but not a guarantee of a universal current limit.
- The 70 μm and 47 μm electrode results show that allowable average charge rate depends strongly on electrode thickness, so a single current value cannot be assumed transferable across laboratory cells.
- Model-derived safe-line values are not the same as directly measured universal limits, so they should be treated as guidance rather than hard thresholds.

#### Missing information

- Exact electrode thickness, areal loading, porosity, and electrolyte composition of the user’s laboratory cell
- Whether a Li/Cu reference electrode or equivalent anode-potential measurement is available
- The exact full seesaw step schedule from the retrieved excerpt
- Cell-specific manufacturer voltage and temperature limits
- Whether the target cell matches the reported 70 μm or 47 μm graphite electrode designs

#### Safety notes

- Do not treat any reported current as universally safe without cell-specific anode-potential verification.
- Use manufacturer voltage and temperature limits as hard stop conditions.
- If anode potential approaches 0 V vs Li/Li+, reduce current immediately; do not continue fixed-current charging.
- A protocol derived from literature is for experimental evaluation only and is not validated for deployment.

#### Follow-up questions

- What are the exact graphite thickness, loading, and porosity of the target laboratory cell?
- Can the cell be instrumented with a Li/Cu reference electrode to measure anode potential during charge?
- What electrolyte and separator are used, and do they match the reported CAMP cells closely enough for transfer?
- Is the goal to maximize average C-rate subject to no-plating, or to minimize risk with a more conservative starting protocol?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | [11] | 0.9209595322608948 | 0.85951331575887 | `soc_2020::chunk::0044` |
| 2 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | [7] | 0.9072295427322388 | 0.8080975785451174 | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044` |
| 3 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Results | [6] | 0.9055352807044983 | 0.7974392531042567 | `pdf_6fec389acaf110ab::chunk::0032` |
| 4 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | [3] | 0.9006848931312561 | 0.7955286825346971 | `doi_10.1149_2.0401906jes::chunk::0013` |
| 5 | Effect of thermal environments on fast charging Li-ion batteries | 3.3 Fast charging capability under different thermal environments | [16] | 0.8838257789611816 | 0.8021409503433756 | `density_2021::chunk::0028` |
| 6 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | [2] | 0.9098140001296997 | 0.8113595277267419 | `pdf_6fec389acaf110ab::chunk::0004` |
| 7 | Optimal Fast Charging Method for a Large-Format Lithium-Ion Battery Based on Nonlinear Model Predictive Control and Reduced Order Electrochemical Model | Table III. Charging times up to 100% SOC at different cycle numbers. | [11] | 0.8972619771957397 | 0.8192444708190463 | `doi_10.1149_1945-7111_a08c3b1a::chunk::0051` |
| 8 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | [13] | 0.8941128849983215 | 0.829637361379332 | `unknown_2020::chunk::0066` |
| 9 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Results | [5] |  |  | `pdf_6fec389acaf110ab::chunk::0031` |
| 10 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Results | [6] |  |  | `pdf_6fec389acaf110ab::chunk::0033` |
| 11 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Results and Discussion | [11] |  |  | `soc_2020::chunk::0043` |
| 12 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | [12] |  |  | `soc_2020::chunk::0045` |
| 13 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | [2, 3] |  |  | `doi_10.1149_2.0401906jes::chunk::0012` |
| 14 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | [3] |  |  | `doi_10.1149_2.0401906jes::chunk::0014` |
| 15 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | [7] |  |  | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0043` |
| 16 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | [7] |  |  | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0045` |

#### Evidence excerpts

**1. `soc_2020::chunk::0044`**

, and elsewhere we use it to prescribe pulse sequences that avoid LPC while providing an average charge rate, well in excess of 4C, that precludes Li-plating. Conclusions Constant current and pulse current charging were conducted on NCM523/Gr cells containing a Li-metal reference electrode at 30 °C, 37 °C, 45 °C, and 55 °C. By repeating the experiment for many C-rates we mapped the currents at which the anode potential (as measured by the reference electrode) reached or crossed zero vs Li/Li + . We used these maps, and a state-of-the art multiphase electrochemical model, to compute the currents at which anode surface potential reaches zero vs Li/Li + , thereby determining the boundary of ...

**2. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044`**

Time to 80% SOC = ± 123.6 min 0.6%. -5°C, Time to 100% SOC = ± 207.0 min 0.9% 4.1. Three-electrode test cell level Taking a look at the current map, the anticipated dependency that the charging current is monotonically increasing with temperature is striking. Inversely, the charging time to 100% SOC increases by tenfold from 45°C to -5°C. The maximum charging current at low SOC goes down from 9C at temperatures of 30°C to 1.1C at -5°C. Interpreting the shape of the current curves in dependency of the SOC in the CVneg phase, the current curves ' slope decreases rapidly at low SOC until it stays almost constant for greater SOCs. At the end of the charging process the current at 45°C goes do...

**3. `pdf_6fec389acaf110ab::chunk::0032`**

from Li plating. The estimated I á ñ for this control is 4.88 C compared to 5.07 C for the optimal 0 a ( ) h = cycle. Results Figure 3. Experimental demonstration of the seesaw ( solid lines ) and potentiostatic ( dashed lines ) charge for a round-2 cell at 30 °C using (a) the 0 a f = control and (b) a f = -25 mV control. The cell was precharged to 16% SOC at a rate of C/3. The pro fi les show the charge to 80% SOC starting from I 0 = 6 C; there are no rests during the seesaw charging. The average current I á ñ during the fast charge is given in the plot. The upper panels show the cell voltage U and the SOC, while the lower panels show the anode reference potential a f and the C-rate duri...

**4. `doi_10.1149_2.0401906jes::chunk::0013`**

qualitative trends observed during fast charging; a more quantitative approach will be taken in subsequent publications. As shown below, RE measurements provide new insights into the phenomenology of Li plating. Experimental Materials.Electrochemical tests were performed using a Gr anode and a Li1.03(Ni0.5Co0.2Mn0.3)0.97O2 (NCM523)cathode.Theanode contained 91.8 wt% graphite (CGP-A12, Philips 66), 2 wt% of carbon black (C45, Timcal), 0.2 wt% oxalic acid and 6 wt% poly(vinylidene difluoride) (PVdF) binder (KF-9300, Kureha). The cathode contained 90 wt% NCM523 (Toda) and 5 wt% of both C45 and PVdF (Solvay 5130). Slurries were coated on battery grade copper and aluminum foils, respectively. ...

**5. `density_2021::chunk::0028`**

, the characteristic length in the cooling direction should be kept small to have a uniform temperature distribution and low cooling needs. 3.3 Fast charging capability under different thermal environments In this subsection, we are going to evaluate the fast-charging performance of LiBs by calculating the battery SOC, at which lithium plating first occurs, vs. the charge rate. For a given thermal environment, the cell is simulated under a consecutive set of charge rates. For each case, the lithium plating potential (LDP) predicted with Eq. (12) is a function of the final SOC. When LDP drops to zero, the corresponding SOC is plotted as that at the onset of Li plating in Fig.5 as dashed li...

**6. `pdf_6fec389acaf110ab::chunk::0004`**

/ % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating Ilya A. Shkrob, Marco-Tulio F. Rodrigues, and Daniel P. Abraham * ,z Chemical Sciences and Engineering Division, Argonne National Laboratory, Lemont, Illinois 60439, United States of America ECS Fast charging of Li-ion batteries would make ' fueling ' of electric vehicles comparable in time to fueling of gasoline-powered cars, increasing consumer appeal of the new technology. Taking the US Department of Energy goal of safe 6 C charging to 80% capacity as a guide, we describe approaches that can mitigate Li plati...

**7. `doi_10.1149_1945-7111_a08c3b1a::chunk::0051`**

ions out of the plated lithium. - Experimental veri fi cation of the protocol in BIL test station. - Reduction of charging time and extension of cycle life. Table III. Charging times up to 100% SOC at different cycle numbers. Compared with 2C CC/CV charging, the charging time is reduced 32% and 25% up to 80% and 100% SOC, respectively and the degradation becomes less after 160 cycles. Future work will include optimization of the fast charging protocol considering the temperature effects and cooling power of battery pack. Appendix A: List of Model Parameters (a: Manufacturers; b: Tuning with the Model; c: Literature)

**8. `unknown_2020::chunk::0066`**

ing protocol. However, several CCCV steps are likely needed as the higher loading cell is more prone to lithium plating, increasing implementation complexity compared to the voltage ramping protocol. Conclusions In this work, the Pseudo2D electrochemical battery model was used to screen traditional fast charging protocols for a moderate HEV loading (2.5 mAh cm -2 ) graphite/NMC 532 cell. The simulation results showed that in terms of the maximum driving force for lithium plating, CCCV and CPCV protocols outperform the multistage constant-current charging with a single voltage cutoff and the pulse charging. To prevent lithium plating, the 5C + constant-current charging stage should be term...

**9. `pdf_6fec389acaf110ab::chunk::0031`**

was ∼ 30% higher than the standard estimate given in Table I, which resulted in lower anode resistance and higher I á ñ than that predicted in Fig. 2b. Results Figure 4a shows the effect of introducing a 300 s rest interval d between the charge steps (this can be compared to Fig. S2). Our model suggests that this time period is suf fi ciently long for the potentials to relax between the charge pulses, and that the resulting average current I ( ) d á ñ is expected to increase with the duration of rest. As the rest period δ increases from 0 to 300 s (see Fig. 4b and animated plots in Fig. S7), the I ( ) d á ñ increases (compare with Fig. S3b), eventually reaching 4.54 C for the 0 a f = cont...

**10. `pdf_6fec389acaf110ab::chunk::0033`**

, and the green line is the added lithiation x (equal to SOC change). The black dashed horizontal lines indicate the zero anode reference potential 0 . a ( ) f = Results Figure 4. (a) Like the seesaw charging in Fig. 3a, but with δ = 300 s rests between the current steps. The I ( ) d á ñ gives the average current excluding the rest periods. (b) The average current I ( ) d á ñ during fast charging experiment in Fig. 3 plotted vs the rest period duration δ between the current steps for two control conditions, corresponding to Figs. 3a and 3b, respectively. The solid lines in panel b are guides to the eye. for the a f = -25 mV control (Fig. 4b). Obviously, this increased average current duri...

**11. `soc_2020::chunk::0043`**

migration in the LiCx electrode accelerates significantly at high rates when the graphite lattice becomes strained. It was impossible to model the fast charge regimes without taking this effect into account. Results and Discussion Figures 14a and 14b present simulations of the ' safe lines ' in Figures 10a and 10b. Using the model, we calculated the ' safe line ' for the anode surface potential η a which is not accessible experimentally. As seen from the plot, due to potential drop across the electrolyte- fi lled separator, the difference between the crossing currents corresponding to these anode potentials systematically increases with the current rate. The overall shape of these ' safe ...

**12. `soc_2020::chunk::0045`**

on the graphite anode) with lower C-rates, thinner electrodes, and higher temperatures (see Fig. 12). For a 70 μ m thick electrode, full cell capacity can Conclusions Figure 14. A numerical simulation of the ' safe lines ' shown in Fig. 10 plotted over an extended range in both axes. The crossing (a) times and (b) lithiation x transferred by a rectangular pulse applied at 3.57 V are plotted vs the charge C-rate ( the vertical axis ). The empty and fi lled symbols are for the anode reference and surface potentials, respectively, for 30 °C ( circles ) and 45 °C ( squares ). The difference between the two potentials increases with the C-rate. For a fi xed time/ lithiation, the C-rates below ...

**13. `doi_10.1149_2.0401906jes::chunk::0012`**

offset can be minimized by using a highly conductive electrolyte and further reduced by placing the RE very close to the electrode (e.g., by using a Luggin capillary). 4 Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials There is a vast literature on cell configurations for 3-electrode tests in Li-ion batteries, mostly in the context of electrochemical impedance spectroscopy (EIS). 11,16-20 As the a.c. currents are low, the EIS experimental designs are flexible, and artifacts arising from improperly constructed REs are easily identifiable. Validating electrode potentials for Li-ion cells operated in realistic d.c. current regim...

**14. `doi_10.1149_2.0401906jes::chunk::0014`**

at 120°C for 12 h before cell assembly. The cells contained 1.6 mL of liquid electrolyte, which exceeds the combined pore volumes of the electrodes and separators. Experimental Most of the tests used a 1.2 mol/dm 3 lithium hexafluorophosphate (LiPF6) in a 3:7 wt/wt mixture of ethylene and ethyl methyl carbonates ('Gen2,' Tomiyama) as electrolyte. In some experiments, 0.7 M of lithium bis(oxalate)borate (LiBOB) was used as the electrolyte salt instead of 1.2 M LiPF6. In the following narrative, these cells are referred to as LiPF6 and LiBOB cells, respectively.

**15. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0043`**

, Time to 100% SOC = ± 59.6 min 2.7%. 10°C, Time to 80% SOC = ± 48.2 min 1.3%. 4.1. Three-electrode test cell level 10°C, Time to 100% SOC = ± 78.8 min 1.9%. 5°C, Time to 80% SOC = ± 63.2 min 1.4%. 5°C, Time to 100% SOC = ± 104.0 min 1.6%. 0°C, Time to 80% SOC = ± 87.1 min 1.3%. 0°C, Time to 100% SOC = ± 145.7 min 1.4%. -5°C, Time to 80% SOC = ± 123.6 min 0.6%. -5°C, Time to 100% SOC = ± 207.0 min 0.9%

**16. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0045`**

1C. The shape of the curves mainly depends on the present surface concentration of lithium of the graphite particles and the slow di ff usion of lithium inside the solid particles. 4.1. Three-electrode test cell level Table 2 indicates the charging times at the di ff erent ambient temperatures. A charging time for a charge from 0% to 80% SOC in less than 15min without lithium deposition is possible for ambient temperatures greater than or equal to 40°C at three-electrode test cell level. Regarding the battery's system limit of 5C, at pouch cell level 80% SOC is reached in 13.9min (test setup A, ∇ = f 0% ), 15.2min (test setup B, ∇ = f 10% ) or 15.6min (test setup C, ∇ = f 10% , = ΔSOC 2% ...

---
