# Evidence-informed reasoning — Queries 2 and 3 live comparison

- Generated: 2026-09-03T21:02:25.488899+00:00
- Mode: `live`
- Model: `gpt-5.4-mini`
- Query count: 2
- Branch/version: `codex/evidence-informed-reasoning`
- Output ceiling: 6,000 tokens
- Purpose: rerun the identical Query 2 and Query 3 wording after permitting disclosed evidence-informed transfer and engineering judgment.

The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.

## Cross-version summary

| Source query | Concrete protocol v1 | Structured protocol v2 | Evidence-informed reasoning |
|---|---|---|---|
| Q2 — NMC811 pouch cell | `pass_with_warnings`; 104.21 s | Error; malformed JSON at 6,000 tokens | **`pass_with_warnings`; 132.57 s; 2 concrete protocols** |
| Q3 — NCM523 laboratory cell | `pass_with_warnings`; 97.54 s | Error; unsupported transfer anchors | **Error; 105.95 s; five inferred values mislabeled as reported** |

Q2 demonstrates the intended policy change: the agent selected measurable currents through disclosed, low-confidence engineering judgment and produced an experimental validation plan rather than leaving every unmatched value unresolved. Its four warnings concern vague language in stop conditions, so the output passed but still requires review.

Q3 failed for a different and appropriate reason. Reasoning was allowed, but the model described five temperature or transition values as directly reported even though those exact values were absent from their cited passages. The validator did not reject inference; it rejected inaccurate provenance labeling. The automatic repair attempt did not successfully relabel or replace those fields.

The result suggests that the revised evidence policy is directionally effective, while the repair prompt still needs to make a narrower correction: change unsupported `reported` fields to `evidence_informed_transfer` or `engineering_judgment` with the required disclosure, instead of regenerating the complete response.

## Query 2: Evidence-informed reasoning — Specific NMC811 pouch-cell target

### Exact query

> Propose an evidence-supported starting fast-charge protocol for a 5 Ah graphite/NMC811 pouch cell at 25 °C, charging from 10% to 80% SOC with a target time of 20 minutes while limiting lithium plating. Give current stages and transition criteria only when supported, and clearly identify values that cannot be determined from the evidence.

### Intended test

Evidence-informed reasoning: whether the system produces one usable experimental starting protocol while distinguishing reported values, evidence-informed transfer, engineering judgment, and unresolved parameters.

### Supplied operating conditions

- chemistry: graphite/NMC811
- form_factor: 5 Ah pouch cell
- temperature: 25 °C
- soc_range: 10-80%
- objective: target 20 minutes while limiting lithium plating

### Execution and validation

- Validation: `pass_with_warnings`
- Warnings: 4
- Agent rounds: 4
- Tool calls: 7
- JSON repair attempts: 1
- Input tokens: 26928
- Output tokens: 10976
- Total tokens: 37904
- Elapsed seconds: 132.57
- Retrieved chunks retained: 16
- Distinct papers retained: 8

#### Validation warnings

- protocol_suggestions[1].protocol_steps[1] contains vague operational language
- protocol_suggestions[1].protocol_steps[2] contains vague operational language
- protocol_suggestions[2].protocol_steps[1] contains vague operational language
- protocol_suggestions[2].protocol_steps[2] contains vague operational language

### Generated answer

Evidence supports a conservative, experimentally testable fast-charge starting protocol for a graphite/NMC811 5 Ah pouch cell at 25 °C, but not a fully reported protocol for the exact target. The literature most directly supports the design direction: high current at low SOC, reduced current at higher SOC, and a voltage ceiling near 4.1 V for plating avoidance in a related graphite/NMC cell. Because the exact chemistry, capacity, and SOC window are not directly reported, the current values below are engineering judgments informed by related studies.

#### Protocol suggestions

**1. Two-stage CC fast charge with a conservative taper to reduce lithium-plating risk while aiming for 10%→80% SOC in about 20 minutes.**

- Designation: `primary`
- Protocol status: `experimental_starting_protocol`
- Origin: `synthesized`
- Confidence: `low`
- Rationale: The protocol is synthesized from three evidence threads. First, graphite/NMC fast-charge literature indicates that current should be higher at low SOC and lower at higher SOC to reduce lithium-plating risk; model work also favors multi-step CCCV or voltage-ramping concepts over a single high-current stage. Second, a graphite/NMC model study states that a 5C+CC stage should be terminated below 4.1 V for a 2.5 mAh cm^-2 cell to avoid plating, which is the closest directly stated voltage ceiling available. Third, a large pouch-cell current map shows that allowable current decreases strongly as SOC rises, supporting a two-stage structure rather than a single constant current. Because no cited source directly reports a 5 Ah graphite/NMC811 pouch-cell protocol at 25 °C from 10% to 80% SOC, the current magnitudes and the 4.2 V upper bound in Stage 2 are experimental assumptions rather than reported values.
- Target conditions: chemistry=graphite/NMC811; form_factor=5 Ah pouch cell; capacity_ah=5; temperature_c=25; start_soc_percent=10; end_soc_percent=80; target_time_minutes=20
- Extrapolation used: True
- Limitations: No cited source directly reports a complete protocol for graphite/NMC811 5 Ah pouch cells at 25 °C from 10% to 80% SOC.; The 3.0C and 1.5C currents are engineering judgments, not reported values.; The 4.20 V upper bound in Stage 2 is transferred from a different chemistry and should be treated as provisional.; The evidence does not establish that 20 minutes is achievable for this exact cell without plating; it only supports a plausible starting point for evaluation.
- Evidence chunks: `10.1149/1945-7111/ab8c84::chunk::0066`, `10.1149/1945-7111/ab8c84::chunk::0065`, `10.1149/1945-7111/abd609::chunk::0004`, `10.1016/j.jpowsour.2019.04.047::chunk::0044`, `10.1016/j.applthermaleng.2017.09.068::chunk::0019`

##### Candidate protocol table

| Stage | Mode | Start | Current | Voltage limit | Temperature limit | Transition |
|---:|---|---|---|---|---|---|
| 1. Initial constant-current charge | CC | Start at 10% SOC and 25 °C cell temperature. | 3.0 C (engineering_judgment) | 4.1 V (evidence_informed_transfer) | 25 C (reported) | voltage >= 4.1 V (evidence_informed_transfer) |

- Stage 1 monitoring: Cell voltage; Cell temperature; dV/dt trend; If available, anode-potential proxy or reference-electrode measurement; Signs of abnormal polarization or rapid voltage rise
- Stage 1 stop conditions: Stop or reduce current if voltage exceeds the cell manufacturer limit or if cell-specific monitoring indicates plating risk.; Stop if temperature departs from the controlled 25 °C condition beyond the lab-defined tolerance.; Stop if voltage rises unusually fast relative to prior characterization of the same cell type.

| 2. Reduced-current finish to 80% SOC | CC | Begin immediately after Stage 1 transition at 4.10 V or earlier if risk indicators appear. | 1.5 C (engineering_judgment) | 4.2 V (engineering_judgment) | 25 C (reported) | SOC >= 80 % (reported) |

- Stage 2 monitoring: SOC estimate from coulomb counting plus voltage consistency check; Cell voltage; Cell temperature; Any sign of accelerated polarization near the end of charge
- Stage 2 stop conditions: Stop at 80% SOC.; Stop earlier if voltage reaches the manufacturer limit or if cell-specific monitoring suggests plating risk.; Stop if temperature control cannot be maintained at 25 °C within the lab tolerance.

##### Extrapolation disclosure

- Justification: The evidence supports the charging-shape principle and approximate voltage ceiling, but not the exact current values for the target cell. Therefore the protocol transfers the structure and uses conservative current assumptions to create a testable starting point.
- Source conditions: Graphite/NMC532 or NMC523 pouch-cell and model studies at 30 °C or unspecified temperatures; 51 Ah pouch-cell current maps; 25 °C pouch-cell fast-charge experiments on different chemistries.
- Target conditions: Graphite/NMC811; 5 Ah pouch cell; 25 °C; 10% to 80% SOC
- Key differences: Chemistry differs: NMC811 target vs NMC532/NMC523/NMC622 sources.; Form factor differs: 5 Ah pouch target vs single-layer lab cells and a 51 Ah pouch cell source.; Temperature differs: target fixed at 25 °C vs some sources at 30 °C or unspecified.; SOC window differs: target 10% to 80% vs some sources 0% to 80% or 0% to 90%.

##### Validation plan

- Measure anode potential or a validated plating proxy during the first experiments if available.
- Run a short matrix around the proposed initial current (e.g., 2.0C, 3.0C, 4.0C) while holding the same 4.10 V transition criterion to determine the highest plating-free current for this exact cell.
- Check whether the 1.5C finish stage is sufficient to reach 80% SOC within 20 minutes; if not, adjust only after confirming no plating signatures.
- Inspect post-charge cells for plating indicators using cell-specific diagnostics such as voltage relaxation behavior, impedance change, or teardown on sacrificial samples.
- Confirm the manufacturer voltage and temperature limits before any test.

**2. More aggressive two-stage CC protocol to probe the 20 min target, using a higher initial current and a stronger taper; this is materially different because it prioritizes time-to-80% more strongly and should only be tested if the primary protocol is too conservative.**

- Designation: `alternative`
- Protocol status: `experimental_starting_protocol`
- Origin: `synthesized`
- Confidence: `low`
- Rationale: This alternative is intentionally more aggressive than the primary protocol to test whether the 20 minute target is feasible. It uses the same evidence-supported structure—high current at low SOC, reduced current at higher SOC, and a voltage ceiling near 4.1 V for plating avoidance—but raises the initial and finishing currents. The 4.0C/2.0C values are not reported in the cited literature; they are engineering judgments informed by the demonstrated ability of a different graphite/NMC cell to average 4.97C to 80% at 30 °C under anode-potential control and by model evidence that current should taper with SOC to avoid plating.
- Target conditions: chemistry=graphite/NMC811; form_factor=5 Ah pouch cell; capacity_ah=5; temperature_c=25; start_soc_percent=10; end_soc_percent=80; target_time_minutes=20
- Extrapolation used: True
- Limitations: No cited source directly supports 4.0C then 2.0C for graphite/NMC811 at 25 °C.; The 4.20 V upper bound is transferred from a different chemistry and should be treated as provisional.; This protocol may exceed the safe plating-free current for the target cell; it is only a starting hypothesis for controlled evaluation.
- Evidence chunks: `10.1149/1945-7111/abd609::chunk::0004`, `10.1149/1945-7111/ab8c84::chunk::0066`, `10.1149/1945-7111/ab8c84::chunk::0065`, `10.1016/j.jpowsour.2019.04.047::chunk::0044`

##### Candidate protocol table

| Stage | Mode | Start | Current | Voltage limit | Temperature limit | Transition |
|---:|---|---|---|---|---|---|
| 1. High-current initial charge | CC | Start at 10% SOC and 25 °C cell temperature. | 4.0 C (engineering_judgment) | 4.1 V (evidence_informed_transfer) | 25 C (reported) | voltage >= 4.1 V (evidence_informed_transfer) |

- Stage 1 monitoring: Cell voltage; Cell temperature; Voltage relaxation after brief interruptions if available; Anode-potential proxy if available; Signs of abnormal polarization
- Stage 1 stop conditions: Stop if voltage exceeds the manufacturer limit or if plating indicators appear.; Stop if temperature control at 25 °C is lost.; Stop if the cell cannot sustain the current without excessive polarization.

| 2. Reduced-current finish to 80% SOC | CC | Begin after Stage 1 transition at 4.10 V or earlier if risk indicators appear. | 2.0 C (engineering_judgment) | 4.2 V (engineering_judgment) | 25 C (reported) | SOC >= 80 % (reported) |

- Stage 2 monitoring: SOC estimate; Cell voltage; Cell temperature; Polarization trend; Any plating proxy available
- Stage 2 stop conditions: Stop at 80% SOC.; Stop earlier if voltage reaches the manufacturer limit or if cell-specific diagnostics suggest plating risk.; Stop if the cell temperature cannot be held at 25 °C.

##### Extrapolation disclosure

- Justification: The alternative probes the upper end of plausible current while retaining the same plating-avoidance logic. It is suitable only as a controlled experimental comparison, not as a validated recipe.
- Source conditions: Different graphite/NMC chemistries and cell sizes, including NCM523/graphite, NMC532/graphite, NMC622/graphite, and a 51 Ah pouch cell.
- Target conditions: Graphite/NMC811; 5 Ah pouch cell; 25 °C; 10% to 80% SOC
- Key differences: Higher initial current than the primary protocol.; Higher finish current than the primary protocol.; Greater risk of plating or thermal stress if the target cell is more polarizable than the source cells.

##### Validation plan

- Compare this alternative against the primary protocol on sacrificial cells only after the primary protocol is characterized.
- Measure whether the cell reaches 80% SOC within 20 minutes and whether any plating proxy worsens relative to the primary protocol.
- If plating indicators appear, revert to the primary protocol or lower the current.
- Use post-charge diagnostics to confirm whether the higher current causes unacceptable degradation.
- Confirm manufacturer voltage and temperature limits before testing.

#### Conflicting evidence

- One model study suggests that achieving 80% in 10 min may require higher temperature or advanced electrode architecture even with optimized protocols, implying that a 20 min target at 25 °C may still be challenging for the target cell.
- The literature includes both model-based protocols and experimental protocols on different chemistries and cell sizes; their current limits are not directly interchangeable.
- A 4.2 V upper bound appears in one NMC622/graphite reference protocol, but a different graphite/NMC model study recommends terminating a 5C+CC stage below 4.1 V to avoid plating, so the safer transferred ceiling is 4.1 V for the initial stage.

#### Missing information

- Direct plating-free fast-charge data for graphite/NMC811 pouch cells at 25 °C.
- Cell-specific voltage-current response, internal resistance, and anode-potential behavior for the exact 5 Ah pouch cell.
- Manufacturer voltage and temperature limits for the target cell.
- Whether 20 minutes from 10% to 80% SOC is achievable without plating for this exact cell.
- A directly reported current schedule for the exact chemistry, capacity, and SOC window.

#### Safety notes

- Do not treat the proposed currents or voltage ceilings as validated for deployment.
- Use cell-specific monitoring, manufacturer limits, and sacrificial validation cells before any broader testing.
- If anode-potential measurement is available, it should govern plating-risk assessment more directly than cell voltage alone.
- If temperature rises or voltage polarization becomes abnormal, reduce current or stop the test.
- The protocol is for controlled laboratory evaluation only and should not be issued as a command to charging hardware.

#### Follow-up questions

- What is the target cell’s manufacturer maximum charge voltage and recommended fast-charge current?
- Can the cell be instrumented with a reference electrode or another plating proxy?
- What is the measured DC resistance and voltage response of the exact 5 Ah NMC811 pouch cell at 25 °C?
- Is the 20 minute target a hard requirement, or can the protocol prioritize plating avoidance over time?
- Are there any cell-specific thermal constraints that would justify a temperature different from 25 °C?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | (13,) | 0.9013583064079285 | 0.7812369350713122 | `10.1149/1945-7111/ab8c84::chunk::0067` |
| 2 | Fast-charging investigation on high-power and high-energy density pouch cells with 3D-thermal model development | 2.4. Charging protocol | (3,) | 0.8979406356811523 | 0.7936518690039538 | `10.1016/j.applthermaleng.2017.09.068::chunk::0019` |
| 3 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) | 0.8936776518821716 | 0.7785172590387278 | `10.1149/1945-7111/abd609::chunk::0004` |
| 4 | Extreme Fast Charge Challenges for Lithium-ion Battery: Variability and Positive Electrode Issues | Experimental | (5,) | 0.8862230181694031 | 0.8003765099165956 | `10.1149/2.0731910jes::chunk::0008` |
| 5 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Discussion | (11,) | 0.8810731768608093 | 0.7963032295618625 | `10.1149/1945-7111/ab8c84::chunk::0057` |
| 6 | Investigation of Temperature and Pressure Behaviour of Constrained Lithium Ion Cell under Lithium Plating Conditions | Results and Discussion | (11,) | 0.8936524391174316 | 0.8149727752662902 | `10.1149/1945-7111/aba550::chunk::0049` |
| 7 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | (7,) | 0.8769049644470215 | 0.7978574825181449 | `10.1016/j.jpowsour.2019.04.047::chunk::0044` |
| 8 | Aging-Optimized Fast Charging of Lithium Ion Cells Based on Three-Electrode Cell Measurements | 2.4. CC -CC -CV Fast Charging (Boost Charging) | (4,) | 0.8723859786987305 | 0.8050720243649417 | `10.1002/ente.202000457::chunk::0019` |
| 9 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Conclusions | (13,) | 0.8675789833068848 | 0.8177454067856902 | `10.1149/1945-7111/ab8c84::chunk::0066` |
| 10 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 4. Conclusion | (12,) | 0.8651597499847412 | 0.8034717586112112 | `10.1016/j.apenergy.2020.115232::chunk::0061` |
| 11 | You may also like | Discussion | (12, 13) |  |  | `10.1149/1945-7111/ab8c84::chunk::0065` |
| 12 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | You may also like | (1,) |  |  | `10.1149/1945-7111/abd609::chunk::0003` |
| 13 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) |  |  | `10.1149/1945-7111/abd609::chunk::0005` |
| 14 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 3.3. Experimental results and analysis. | (12,) |  |  | `10.1016/j.apenergy.2020.115232::chunk::0060` |
| 15 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 4. Conclusion | (13,) |  |  | `10.1016/j.apenergy.2020.115232::chunk::0062` |
| 16 | Aging-Optimized Fast Charging of Lithium Ion Cells Based on Three-Electrode Cell Measurements | 2.5. CC -CV Reference Charging | (4,) |  |  | `10.1002/ente.202000457::chunk::0020` |

#### Evidence excerpts

**1. `10.1149/1945-7111/ab8c84::chunk::0067`**

achieve fast charging without lithium plating, the cell should be charged at a higher current when the cell voltage is low, and charged to higher voltage when the charge current is low. Conclusions Based on the features of the semi-optimal protocol, two practical novel fast charging protocols were proposed, namely the voltage ramping protocol and the multiple CCCV protocol. The simulation results showed that for the 2.5 mAh cm -2 cell, the maximum capacity after 10 min charge at 30 °C without lithium plating can be improved by up to 10.7% using the proposed protocols compared with the standard CCCV protocol. To achieve 80% charge in 10 min, the proposed protocols will require a charging t...

**2. `10.1016/j.applthermaleng.2017.09.068::chunk::0019`**

current of negative pulse has been selected, in this work, to the same frequency, 20 mHz, in order to a comparative study regard the thermal effect on pouch cells. 2.4. Charging protocol The proposed sequence for the data collection procedure for fast-charging test for which the experimental test shown in Fig. 1 is used, is described in Fig. 2. After a preconditioning test consisting of three complete charge-discharge cycles at 25 ° C to 10% state-ofcharge (SoC); the cell is tempered at the tested temperature. Then, one of the fast-charging profile described abode is applied for the cell to reach 90% SoC. After each fast-charging test, the cell is completely discharged at 25 ° C with a 1C...

**3. `10.1149/1945-7111/abd609::chunk::0004`**

/ % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating Ilya A. Shkrob, Marco-Tulio F. Rodrigues, and Daniel P. Abraham * ,z Chemical Sciences and Engineering Division, Argonne National Laboratory, Lemont, Illinois 60439, United States of America ECS Fast charging of Li-ion batteries would make ' fueling ' of electric vehicles comparable in time to fueling of gasoline-powered cars, increasing consumer appeal of the new technology. Taking the US Department of Energy goal of safe 6 C charging to 80% capacity as a guide, we describe approaches that can mitigate Li plati...

**4. `10.1149/2.0731910jes::chunk::0008`**

charging. These issues are often overlooked due to the focus on Li metal plating during fast charging, but have the potential to significantly impact the eventual application and use of fast charging. Experimental Table I lists the material, electrode, cell design parameters, and Table II includes the charging protocols. Graphite (1506T Superior Graphite) and NMC532 (Toda America) were used as respective negative and positive electrode active materials, respectively, to fabricate electrodes at the Cell Analysis, Modeling, and Prototyping (CAMP) Facility at Argonne National Laboratory (Argonne). These electrodes were cut and assembled in single layer pouch cells with Celgard 2320 separator...

**5. `10.1149/1945-7111/ab8c84::chunk::0057`**

ating capacity can be further increased by using a higher initial C rate, it is likely to trigger degradation mechanisms other than lithium plating, such as cathode cracking and excessive heat generation. Discussion Achieve 80% charge in 10 min at elevated temperature. -Figure 8 shows that the investigated moderate loading cell can only be charged to SOC = 74.1% within 10 min even when the semioptimal protocol is used, when the ambient temperature is T 0 = 30 °C. To achieve the goal of charging 80% in 10 min, the proposed fast charging protocols need to be combined with other measures, such as using electrodes with advanced architecture or charging the cell at a higher temperature. The la...

**6. `10.1149/1945-7111/aba550::chunk::0049`**

the stepwise protocol is reduced to the next lower current before lithium deposition onset is reached. The resulting fast charging protocol based on onset of lithium deposition is shown in Table II. Results and Discussion The shown fast charge protocol allows a charging of the cell from 0%SoC to 85%SoC in 26.8 min. To validate the developed charging protocol three cells were cycled with this protocol. Start condition was 25 °C ±1 °C cell temperature and the temperature of the chamber held constant. Cells were cycled in the already presented test setup (refer to Fig. 1) to realize the same test conditions as in second test case. The cycling was started at 0%SoC and the cell was charged wit...

**7. `10.1016/j.jpowsour.2019.04.047::chunk::0044`**

Time to 80% SOC = ± 123.6 min 0.6%. -5°C, Time to 100% SOC = ± 207.0 min 0.9% 4.1. Three-electrode test cell level Taking a look at the current map, the anticipated dependency that the charging current is monotonically increasing with temperature is striking. Inversely, the charging time to 100% SOC increases by tenfold from 45°C to -5°C. The maximum charging current at low SOC goes down from 9C at temperatures of 30°C to 1.1C at -5°C. Interpreting the shape of the current curves in dependency of the SOC in the CVneg phase, the current curves ' slope decreases rapidly at low SOC until it stays almost constant for greater SOCs. At the end of the charging process the current at 45°C goes do...

**8. `10.1002/ente.202000457::chunk::0019`**

2.4. CC -CC -CV Fast Charging (Boost Charging) limits, a charging protocol with a time equivalent mean current was applied (see Figure 2). This means that a current was applied so that the time it takes to charge from 0% SoC to 80% SoC should be identical to the multistep charging profile. When 80% SoC or the maximum cell voltage was reached, the charging continued with 1 C to the maximum cell voltage of 4.2 V and a CV phase to C/20. Between charge and discharge steps, there were always 10 min rest periods. During aging testing, the protocol was again programmed to keep the charging time from 0% to 80% SoC constant. Every 50 cycles a characterization was applied and the SoH was measured. ...

**9. `10.1149/1945-7111/ab8c84::chunk::0066`**

ing protocol. However, several CCCV steps are likely needed as the higher loading cell is more prone to lithium plating, increasing implementation complexity compared to the voltage ramping protocol. Conclusions In this work, the Pseudo2D electrochemical battery model was used to screen traditional fast charging protocols for a moderate HEV loading (2.5 mAh cm -2 ) graphite/NMC 532 cell. The simulation results showed that in terms of the maximum driving force for lithium plating, CCCV and CPCV protocols outperform the multistage constant-current charging with a single voltage cutoff and the pulse charging. To prevent lithium plating, the 5C + constant-current charging stage should be term...

**10. `10.1016/j.apenergy.2020.115232::chunk::0061`**

% SOC = 6.08 min. OFC-T, 80% SOC = 18.01 min. OFC-T, 100% SOC = 47.91 min 4. Conclusion An online optimal fast charging method was proposed based on a reduced electrochemical model that embeds submodels for side reaction, lithium plating and stripping as a function of temperature. The experimentally validated models are used to analyze the effects of Crates and temperature on the side reaction and lithium plating and then find out the optimal temperatures at different C-rates. At the optimal temperatures, the battery has the longest cycling life. Then, the nonlinear model predictive control is used to determine charging currents and operating temperatures. In order to recover the ions out...

**11. `10.1149/1945-7111/ab8c84::chunk::0065`**

plating capacity to SOC = 70.8% after 10 min charge, which is 18.6% higher than that of the standard CCCV protocol at the same temperature. Discussion It should be noted that at high temperature other degradation mechanisms may be more signi fi cant than lithium plating. It is not well understood what temperature is acceptable for the fast charging process. If the battery can be warmed and cooled in a few minutes, then fast charging may be carried out at relatively high temperature without much detrimental lifetime effects/SEI damage. This has been demonstrated 16 in low capacity cells with modest energy density where temperature is easily modulated, but whether this can be done in large ...

**12. `10.1149/1945-7111/abd609::chunk::0003`**

sealed battery test cell! For precise long-term measurements of solid-state cell chemistries Learn more on our product website: Download the data sheet (PDF): You may also like Half cell SiC480 + LPSCI vs. In/lnLi Coulombic efficiency / % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com

**13. `10.1149/1945-7111/abd609::chunk::0005`**

accounts for these observations and provides a means to extrapolate the approach to other cell designs and operation regimes, drawing the maximum average fast charging rates that can still avoid Li plating. Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating © 2021 The Author(s). Published on behalf of The Electrochemical Society by IOP Publishing Limited. This is an open access article distributed under the terms of the Creative Commons Attribution 4.0 License (CC BY, http://creativecommons.org/licenses/ by/4.0/), which permits unrestricted reuse of the work in any medium, provided the original work is properly cited. [DOI: 10.1149/ 1945-7111/...

**14. `10.1016/j.apenergy.2020.115232::chunk::0060`**

closest to that of 1 C CC/ CV charging. The above analysis s that the design FC protocol (OFC-T) significantly reduces the charging time and degradation speed. 3.3. Experimental results and analysis. Table 5 Charging time at different SOC intervals using different charging protocols. CC/CV (1 C), 40% SOC = 23.23 min. CC/CV (1 C), 80% SOC = 46.67 min. CC/CV (1 C), 100% SOC = 78.13 min. CC/CV (2 C), 40% SOC = 11.63 min. CC/CV (2 C), 80% SOC = 26.37 min. CC/CV (2 C), 100% SOC = 52.60 min. CC/CV (2.7 C), 40% SOC = 9.33 min. CC/CV (2.7 C), 80% SOC = 17.73 min. CC/CV (2.7 C), 100% SOC = 48.60 min. CC/CV (3 C), 40% SOC = 7.73 min. CC/CV (3 C), 80% SOC = 15.83 min. CC/CV (3 C), 100% SOC = 45.60 m...

**15. `10.1016/j.apenergy.2020.115232::chunk::0062`**

reaction rate becomes less but the lithium plating rate increases. Fig. 13. Comparison of different charging protocols. (a) Charging protocols; (b) capacity fade. 4. Conclusion - Active variation of operating temperature along with current profiles optimized by nonlinear model predictive control significantly enables extension of cycle life by suppressing side reaction and lithium plating. - Since pulse discharging current promotes the lithium stripping and recovers ions out of the plated lithium, a higher charging current can be applied than that commonly derived by limiting the overpotential to prevent lithium plating. Therefore, the charging time is further reduced without imposing any...

**16. `10.1002/ente.202000457::chunk::0020`**

applied and the SoH was measured. For the following cycles, the current for the step from 0% to 80% SoC was scaled down according to Equation (1). 2.5. CC -CV Reference Charging As a reference for both fast charging procedures aging cycles with 1 C charge current were conducted (see Figure 2). Here, the cells were charged with 1 C CC to the maximum cell voltage of 4.2 V followed by a CV phase to C/20. Afterward, the cells were www.entechnol.de discharged again with 1 C CC to 3 V. Between charge and discharge steps, there were always 10 min rest periods. After aging testing, selected cells were discharged to 3 V and opened in an argon-filled glovebox. The cell components were separated and...

---

## Query 3: Evidence-informed reasoning — Known NCM523 evidence target

### Exact query

> Using retrieved experimental evidence, describe a starting fast-charge protocol design for an NCM523/graphite laboratory cell at 30 °C over 0-80% SOC that is intended to avoid lithium plating. Distinguish directly reported protocol elements from synthesis and inference.

### Intended test

Evidence-informed reasoning: whether known Part V evidence can support a measurable protocol through transparent literature transfer or engineering judgment without mislabeling inferred values as reported.

### Supplied operating conditions

- chemistry: NCM523/graphite
- form_factor: laboratory cell
- temperature: 30 °C
- soc_range: 0-80%
- objective: avoid lithium plating

### Execution result

**ERROR:** RuntimeError: LLM protocol remained invalid after one repair attempt: protocol_suggestions[1].protocol_steps[1].temperature_limit reported value was not found in its cited evidence; protocol_suggestions[1].protocol_steps[2].temperature_limit reported value was not found in its cited evidence; protocol_suggestions[2].protocol_steps[1].temperature_limit reported value was not found in its cited evidence; protocol_suggestions[2].protocol_steps[1].transition reported value was not found in its cited evidence; protocol_suggestions[2].protocol_steps[2].temperature_limit reported value was not found in its cited evidence
