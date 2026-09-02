# Concrete protocol version — live comparison evaluation

- Generated: 2026-09-02T19:18:12.400045+00:00
- Mode: `live`
- Model: `gpt-5.4-mini`
- Query count: 1
- Source query evaluated: Query 2 of the original five-query set
- Query 3 status: Not run because Query 2 required 104.21 seconds; stopped according to the requested time limit.
- Prompt/output version: `concrete_protocol_v1`
- Purpose: diagnose retrieval relevance, protocol specificity, analogue transfer, and appropriate refusal.

The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.

## Query 1: Concrete protocol version — Specific NMC811 pouch-cell target

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
| 1 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | (13,) | 0.8786934018135071 | 0.772662716945294 | `unknown_2020::chunk::0067` |
| 2 | Extreme Fast Charge Challenges for Lithium-ion Battery: Variability and Positive Electrode Issues | Experimental | (5,) | 0.875095784664154 | 0.7855472565894285 | `tanim_2015::chunk::0008` |
| 3 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | (13,) | 0.8661078810691833 | 0.7909473915467107 | `unknown_2020::chunk::0066` |
| 4 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Discussion | (11,) | 0.8621857762336731 | 0.7830585657724372 | `unknown_2020::chunk::0057` |
| 5 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Screening of Conventional Protocols Using the Pseudo2D Model | (5,) | 0.8603463768959045 | 0.7971119392408116 | `unknown_2020::chunk::0022` |
| 6 | Investigation of Temperature and Pressure Behaviour of Constrained Lithium Ion Cell under Lithium Plating Conditions | Results and Discussion | (11,) | 0.8933550119400024 | 0.7860342206387982 | `doi_10.1149_1945-7111::chunk::0049` |
| 7 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Screening of Conventional Protocols Using the Pseudo2D Model | (6,) | 0.8865808248519897 | 0.7860154062043826 | `unknown_2020::chunk::0028` |
| 8 | Non-destructive fast charging algorithm of lithium-ion batteries based on the control-oriented electrochemical model | 4. Applying the fast charging algorithm to a commercial lithium-ion battery: experimental validation | (6, 7) | 0.8738889098167419 | 0.8059982232039277 | `pdf_e648a41cdcfc30f1::chunk::0032` |
| 9 | Investigation of Temperature and Pressure Behaviour of Constrained Lithium Ion Cell under Lithium Plating Conditions | Experimental | (3,) | 0.8714893460273743 | 0.8081091472341074 | `doi_10.1149_1945-7111::chunk::0014` |

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
