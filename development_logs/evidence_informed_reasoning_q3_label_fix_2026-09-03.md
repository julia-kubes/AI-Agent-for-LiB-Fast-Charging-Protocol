# Q3 verification — user-specified provenance labeling fix

- Generated: 2026-09-03T21:15:31.763161+00:00
- Mode: `live`
- Model: `gpt-5.4-mini`
- Query count: 1
- Branch/version: `codex/evidence-informed-reasoning`
- Output ceiling: 6,000 tokens
- Purpose: verify that user-supplied temperature and SOC targets are no longer mislabeled as directly reported literature values.

The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.

## Verification result

**Passed with warnings.** The prior Q3 run failed after 105.95 seconds because five temperature or transition values were mislabeled as `reported`. After the fix, Q3 completed in 98.22 seconds without a repair attempt. Every 30 °C stage limit and every 80% SOC endpoint is now labeled `user_specified`.

The generated primary protocol uses a 4 C transferred initial current followed by 2 C and 0.5 C engineering-judgment stages. It is labeled `experimental_starting_protocol`, not a literature-validated protocol. An alternative 5 C / 3 C / 1 C candidate is also supplied.

Eight warnings remain. Six identify vague operational language, and two flag transferred current anchors that were not found verbatim in the cited excerpts. These warnings preserve the need for human review without suppressing the complete candidate protocols.

## Query 3: Evidence-informed reasoning with user-specified labels — Known NCM523 evidence target

### Exact query

> Using retrieved experimental evidence, describe a starting fast-charge protocol design for an NCM523/graphite laboratory cell at 30 °C over 0-80% SOC that is intended to avoid lithium plating. Distinguish directly reported protocol elements from synthesis and inference.

### Intended test

Whether user-supplied 30 °C and 80% SOC values are labeled user_specified rather than reported, and whether unsupported literature claims are relabeled during repair.

### Supplied operating conditions

- chemistry: NCM523/graphite
- form_factor: laboratory cell
- temperature: 30 °C
- soc_range: 0-80%
- objective: avoid lithium plating

### Execution and validation

- Validation: `pass_with_warnings`
- Warnings: 8
- Agent rounds: 3
- Tool calls: 7
- JSON repair attempts: 0
- Input tokens: 9724
- Output tokens: 5966
- Total tokens: 15690
- Elapsed seconds: 98.22
- Retrieved chunks retained: 15
- Distinct papers retained: 7

#### Validation warnings

- protocol_suggestions[1].protocol_steps[1] contains vague operational language
- protocol_suggestions[1].protocol_steps[1].current source value was not found verbatim in its cited evidence; review the transfer rationale
- protocol_suggestions[1].protocol_steps[2] contains vague operational language
- protocol_suggestions[1].protocol_steps[3] contains vague operational language
- protocol_suggestions[2].protocol_steps[1] contains vague operational language
- protocol_suggestions[2].protocol_steps[1].current source value was not found verbatim in its cited evidence; review the transfer rationale
- protocol_suggestions[2].protocol_steps[2] contains vague operational language
- protocol_suggestions[2].protocol_steps[3] contains vague operational language

### Generated answer

Retrieved evidence supports a conservative fast-charge starting design for NCM523/graphite at 30 °C that prioritizes avoiding lithium plating by keeping the anode away from zero potential vs Li/Li+. The strongest directly relevant evidence is from Argonne’s NCM523/graphite three-electrode laboratory-cell studies showing that at 30 °C a 70 μm graphite electrode could be charged to 80% capacity at an average 4.97 C without Li plating, and that thinner graphite electrodes can sustain higher no-plating average rates (7.40 C for 47 μm). The same series reports that charging should avoid simultaneous high current and high voltage, and that pulse/variable-rate protocols can be prescribed from the anode-potential ‘safe line’ to keep the anode potential positive. Because the exact cell thickness, capacity, and reference-electrode instrumentation for the user’s laboratory cell are not specified, the protocol below is an experimental starting protocol with one primary candidate and one materially different alternative, both explicitly labeled where values are reported versus transferred or judgment-based.

#### Protocol suggestions

**1. Anode-potential-guided variable-rate charge to 80% SOC, using a conservative average rate anchored to the 30 °C NCM523/graphite safe-line result and a low-current finish to avoid high-current/high-voltage overlap.**

- Designation: `primary`
- Protocol status: `experimental_starting_protocol`
- Origin: `synthesized`
- Confidence: `medium`
- Rationale: Direct evidence from the Argonne NCM523/graphite series shows that at 30 °C a 70 μm graphite electrode could be charged to 80% capacity at an average 4.97 C without Li plating, and that thinner graphite electrodes can support even higher no-plating rates. The same series emphasizes that the relevant design rule is to avoid low anode potentials, and that pulse/variable-rate charging can be prescribed from the anode-potential safe line. Because the user’s laboratory cell thickness, capacity, and reference-electrode configuration are not specified, the protocol is a conservative experimental starting point: begin with a moderate CC rate below the reported average, taper as SOC rises, and finish at low current while monitoring anode potential if available.
- Target conditions: chemistry=NCM523/graphite; form_factor=laboratory cell; capacity_ah=None; temperature_c=30; start_soc_percent=0; end_soc_percent=80; target_time_minutes=None
- Extrapolation used: True
- Limitations: No exact full-cell voltage cutoff for the user’s specific laboratory cell was retrieved in the allowed evidence set.; The protocol depends on engineering judgment because the cell’s graphite thickness, capacity, and reference-electrode setup are unknown.; The 4.97 C result is directly reported for a specific 70 μm graphite electrode; transferring it to another cell requires caution.; The 0 V vs Li/Li+ plating boundary is a mechanistic criterion, but the exact current schedule to stay above it is not directly reported for the user’s cell.
- Evidence chunks: `10.1149/1945-7111/abd609::chunk::0004`, `10.1149/1945-7111/abb70d::chunk::0044`, `10.1149/1945-7111/abb70d::chunk::0043`, `10.1149/2.0401906jes::chunk::0013`, `10.1149/1945-7111/ab8c84::chunk::0040`

##### Candidate protocol table

| Stage | Mode | Start | Current | Voltage limit | Temperature limit | Transition |
|---:|---|---|---|---|---|---|
| 1. Initial high-acceptance constant-current charge | CC | Begin at 0% SOC and 30 °C after standard rest/conditioning appropriate to the cell. | 4.0 C (evidence_informed_transfer) | Unresolved | 30 C (user_specified) | anode_potential <= 0 V vs Li/Li+ (engineering_judgment) |

- Stage 1 monitoring: Cell voltage; Cell temperature; If available, anode potential vs Li/Li+ using a reference electrode; Current acceptance trend during charge
- Stage 1 stop conditions: Stop or taper current if anode potential approaches 0 V vs Li/Li+; Stop if cell temperature exceeds the lab’s validated limit or manufacturer limit; Stop if cell voltage reaches the validated upper cutoff for this specific cell; Stop if any sign of lithium plating is detected by the lab’s diagnostic method

| 2. Current taper to maintain positive anode potential | CC | Enter when anode potential begins to approach the plating boundary or when cell voltage rises into the high-polarization region. | 2.0 C (engineering_judgment) | Unresolved | 30 C (user_specified) | SOC >= 60 % (engineering_judgment) |

- Stage 2 monitoring: Cell voltage; Cell temperature; Anode potential if available; dV/dt and current acceptance
- Stage 2 stop conditions: Stop tapering and terminate charge if anode potential approaches 0 V vs Li/Li+; Stop if voltage reaches validated upper cutoff; Stop if temperature rises above validated limit; Stop if current acceptance collapses unexpectedly, indicating rising polarization

| 3. Low-current finish to 80% SOC | CC | Begin after the taper stage when the cell is in the upper-SOC region and plating margin is smallest. | 0.5 C (engineering_judgment) | Unresolved | 30 C (user_specified) | SOC >= 80 % (user_specified) |

- Stage 3 monitoring: Cell voltage; Cell temperature; Anode potential if available; Signs of plating in post-test diagnostics
- Stage 3 stop conditions: Terminate at 80% SOC; Terminate earlier if anode potential approaches 0 V vs Li/Li+; Terminate if voltage reaches validated upper cutoff; Terminate if temperature exceeds validated limit

##### Extrapolation disclosure

- Justification: The literature directly supports the mechanism and approximate rate regime, but not the exact current schedule for the user’s unspecified laboratory cell. Therefore the protocol transfers the reported 30 °C no-plating rate downward for conservatism and adds a taper based on the reported safe-line principle.
- Source conditions: NCM523/graphite laboratory cell; 30 °C; 70 μm graphite electrode; average 4.97 C to 80% capacity without Li plating; safe-line concept based on anode potential vs Li/Li+
- Target conditions: NCM523/graphite laboratory cell; 30 °C; 0-80% SOC; unknown electrode thickness/capacity/reference-electrode availability
- Key differences: Unknown graphite thickness and areal loading; Unknown cell capacity; Unknown electrolyte and separator details; Unknown availability/placement of a reference electrode; User target is 0-80% SOC rather than the paper’s specific cell configuration

##### Validation plan

- Measure anode potential vs Li/Li+ with a reference electrode if possible and verify that it remains positive throughout charge.
- Run a short matrix around the primary protocol by varying the initial CC rate modestly (for example, below and above 4.0 C) while holding the taper logic fixed.
- Use post-charge diagnostics sensitive to lithium plating, such as voltage relaxation signatures and cell teardown/analytical confirmation if available.
- If the cell is thinner than the 70 μm reference case, consider increasing the initial rate only after confirming no-plating behavior at 4.0 C.
- If the cell is thicker or more resistive than the reference case, reduce the initial rate further before increasing it.

**2. Pulse/rectangular-rate protocol guided by the reported safe-line concept, using lower average current at 30 °C and explicit current reduction near the upper-SOC region.**

- Designation: `alternative`
- Protocol status: `experimental_starting_protocol`
- Origin: `synthesized`
- Confidence: `low`
- Rationale: This alternative is materially different from the primary because it uses a pulse/rectangular-rate framework rather than a simple CC-to-taper schedule. The literature explicitly supports pulse sequences derived from anode-potential safe lines and reports that average rates well above 4 C can be achieved without plating when the anode potential is controlled. The exact pulse amplitudes and duty cycles are not directly reported for the user’s cell, so the values here are experimental assumptions anchored to the reported 4.97 C average no-plating result at 30 °C.
- Target conditions: chemistry=NCM523/graphite; form_factor=laboratory cell; capacity_ah=None; temperature_c=30; start_soc_percent=0; end_soc_percent=80; target_time_minutes=None
- Extrapolation used: True
- Limitations: No exact pulse timing or duty cycle was retrieved for the user’s cell.; No exact voltage cutoff was retrieved for the user’s cell.; The protocol assumes the lab can monitor anode potential or otherwise detect plating risk in real time.; The 5.0 C and 3.0 C values are not directly reported for this exact cell; they are conservative experimental assumptions.
- Evidence chunks: `10.1149/1945-7111/abd609::chunk::0004`, `10.1149/1945-7111/abb70d::chunk::0044`, `10.1149/1945-7111/abb70d::chunk::0043`, `10.1149/2.0401906jes::chunk::0013`

##### Candidate protocol table

| Stage | Mode | Start | Current | Voltage limit | Temperature limit | Transition |
|---:|---|---|---|---|---|---|
| 1. Pulse charge segment in low-SOC region | other | Begin at 0% SOC and 30 °C. | 5.0 C (evidence_informed_transfer) | Unresolved | 30 C (user_specified) | anode_potential <= 0 V vs Li/Li+ (engineering_judgment) |

- Stage 1 monitoring: Anode potential if available; Cell voltage; Cell temperature; Pulse response and relaxation behavior
- Stage 1 stop conditions: Stop if anode potential approaches 0 V vs Li/Li+; Stop if voltage reaches validated upper cutoff; Stop if temperature exceeds validated limit; Stop if pulse relaxation no longer restores plating margin

| 2. Pulse reduction in mid-SOC region | other | Enter when polarization increases and the anode-potential margin narrows. | 3.0 C (engineering_judgment) | Unresolved | 30 C (user_specified) | SOC >= 60 % (engineering_judgment) |

- Stage 2 monitoring: Cell voltage; Cell temperature; Anode potential if available; Pulse-induced relaxation recovery
- Stage 2 stop conditions: Stop if anode potential approaches 0 V vs Li/Li+; Stop if voltage reaches validated upper cutoff; Stop if temperature exceeds validated limit

| 3. Low-rate finish to 80% SOC | CC | Begin in the upper-SOC region after pulse reduction. | 1.0 C (engineering_judgment) | Unresolved | 30 C (user_specified) | SOC >= 80 % (user_specified) |

- Stage 3 monitoring: Cell voltage; Cell temperature; Anode potential if available; Evidence of plating in post-test diagnostics
- Stage 3 stop conditions: Terminate at 80% SOC; Terminate earlier if anode potential approaches 0 V vs Li/Li+; Terminate if voltage reaches validated upper cutoff; Terminate if temperature exceeds validated limit

##### Extrapolation disclosure

- Justification: The literature supports the design direction but not the exact pulse schedule for the user’s cell; therefore the pulse-average rates are transferred conservatively and the stage transitions are engineering judgments.
- Source conditions: NCM523/graphite laboratory cell; 30 °C; safe-line/pulse-sequence concept; reported 4.97 C average to 80% capacity without Li plating
- Target conditions: NCM523/graphite laboratory cell; 30 °C; 0-80% SOC; unknown cell geometry and instrumentation
- Key differences: Pulse timing not reported for the user cell; Unknown electrode thickness and capacity; Unknown reference-electrode availability

##### Validation plan

- Compare the pulse protocol against the primary CC/taper protocol using the same cell and diagnostics.
- Measure anode potential during pulses to verify that the pulse/rest pattern preserves positive anode potential.
- If plating indicators appear, reduce pulse-average current before changing duty cycle.
- Use the thinner-electrode result in the literature only as an upper-bound reference, not as a direct target for this cell.

#### Conflicting evidence

- The literature reports 4.97 C average to 80% capacity at 30 °C for a 70 μm graphite electrode, but also shows that safe charge rate depends strongly on graphite thickness; a thinner 47 μm electrode reached 7.40 C average without plating. This means the transferable rate for the user’s unspecified laboratory cell is uncertain.
- The safe-line/pulse-sequence papers support avoiding simultaneous high current and high voltage, but they do not provide a single universally valid current schedule for all NCM523/graphite laboratory cells at 30 °C.
- The retrieved evidence set does not provide a directly applicable full-cell voltage cutoff for the user’s exact laboratory cell under the requested conditions.

#### Missing information

- Graphite anode thickness and areal loading
- Cell capacity (Ah)
- Electrolyte composition and separator details
- Whether a Li-reference electrode is available and where it is placed
- Validated upper voltage cutoff for the specific laboratory cell
- Any cell-specific plating diagnostic method or acceptance criterion

#### Safety notes

- Do not treat the transferred current values as directly reported for the user’s cell; they are conservative experimental starting points.
- Use cell-specific manufacturer limits and lab-validated stop criteria for voltage, temperature, and SOC.
- If a reference electrode is available, prioritize anode-potential control and stop before sustained approach to 0 V vs Li/Li+.
- If no reference electrode is available, reduce current further and rely on conservative voltage/temperature limits plus post-test plating diagnostics.

#### Follow-up questions

- What is the graphite anode thickness and cell capacity of the laboratory cell?
- Is a Li-reference electrode available for in situ anode-potential monitoring?
- What full-cell upper cutoff voltage is validated for this specific NCM523/graphite cell?
- What electrolyte and separator are used, and are there known transport limitations?
- What plating-detection method will be used to validate the starting protocol?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) | 0.9261988401412964 | 0.7958814978598161 | `10.1149/1945-7111/abd609::chunk::0004` |
| 2 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (11,) | 0.9166436791419983 | 0.8353739504658118 | `10.1149/1945-7111/abb70d::chunk::0044` |
| 3 | Uncertainty-aware state estimation for electrochemical model-based fast charging control of lithium-ion batteries | 5. Charging control | (9,) | 0.9108880162239075 | 0.795184338097532 | `10.4121/uuid:30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0043` |
| 4 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | (3,) | 0.9101972579956055 | 0.8164476197022036 | `10.1149/2.0401906jes::chunk::0013` |
| 5 | Model-Instructed Design of Novel Charging Protocols for the Extreme Fast Charging of Lithium-Ion Batteries Without Lithium Plating | Novel Charging Protocols Without Lithium Plating | (8,) | 0.9012275338172913 | 0.8039382554520985 | `10.1149/1945-7111/ab8c84::chunk::0040` |
| 6 | Investigation of Temperature and Pressure Behaviour of Constrained Lithium Ion Cell under Lithium Plating Conditions | Experimental | (3,) | 0.8985691666603088 | 0.838915380368828 | `10.1149/1945-7111/aba550::chunk::0014` |
| 7 | Optimal Fast Charging Method for a Large-Format Lithium-Ion Battery Based on Nonlinear Model Predictive Control and Reduced Order Electrochemical Model | Table III. Charging times up to 100% SOC at different cycle numbers. | (11,) | 0.8914435505867004 | 0.8120689148423086 | `10.1149/1945-7111/abd607::chunk::0051` |
| 8 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | You may also like | (1,) |  |  | `10.1149/1945-7111/abd609::chunk::0003` |
| 9 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) |  |  | `10.1149/1945-7111/abd609::chunk::0005` |
| 10 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Results and Discussion | (11,) |  |  | `10.1149/1945-7111/abb70d::chunk::0043` |
| 11 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (12,) |  |  | `10.1149/1945-7111/abb70d::chunk::0045` |
| 12 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | (2, 3) |  |  | `10.1149/2.0401906jes::chunk::0012` |
| 13 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | (3,) |  |  | `10.1149/2.0401906jes::chunk::0014` |
| 14 | You may also like | Novel Charging Protocols Without Lithium Plating | (8,) |  |  | `10.1149/1945-7111/ab8c84::chunk::0039` |
| 15 | You may also like | Novel Charging Protocols Without Lithium Plating | (8,) |  |  | `10.1149/1945-7111/ab8c84::chunk::0041` |

#### Evidence excerpts

**1. `10.1149/1945-7111/abd609::chunk::0004`**

/ % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating Ilya A. Shkrob, Marco-Tulio F. Rodrigues, and Daniel P. Abraham * ,z Chemical Sciences and Engineering Division, Argonne National Laboratory, Lemont, Illinois 60439, United States of America ECS Fast charging of Li-ion batteries would make ' fueling ' of electric vehicles comparable in time to fueling of gasoline-powered cars, increasing consumer appeal of the new technology. Taking the US Department of Energy goal of safe 6 C charging to 80% capacity as a guide, we describe approaches that can mitigate Li plati...

**2. `10.1149/1945-7111/abb70d::chunk::0044`**

, and elsewhere we use it to prescribe pulse sequences that avoid LPC while providing an average charge rate, well in excess of 4C, that precludes Li-plating. Conclusions Constant current and pulse current charging were conducted on NCM523/Gr cells containing a Li-metal reference electrode at 30 °C, 37 °C, 45 °C, and 55 °C. By repeating the experiment for many C-rates we mapped the currents at which the anode potential (as measured by the reference electrode) reached or crossed zero vs Li/Li + . We used these maps, and a state-of-the art multiphase electrochemical model, to compute the currents at which anode surface potential reaches zero vs Li/Li + , thereby determining the boundary of ...

**3. `10.4121/uuid:30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0043`**

at an SOC of 10% and stopped at an SOC of 80% or the beginning of lithium plating. The setpoint of the anode voltage controller is fixed to 1 mV. 5. Charging control The simulation results are depicted in Fig. 5. The left column shows current, anode potential and temperature for controlled charging while the right column depicts the results for CC-charging. The current of the CC-charging scheme was set to the average current of the controlled charging simulations, which is approximately 2.1 C at 0 � C and 1.7 C at -5 � C, resulting in similar charging overall times. This charging speed is also above the specified 2 C which are allowed above 0 � C. An SOC of 80% was reached after 22 and 29...

**4. `10.1149/2.0401906jes::chunk::0013`**

qualitative trends observed during fast charging; a more quantitative approach will be taken in subsequent publications. As shown below, RE measurements provide new insights into the phenomenology of Li plating. Experimental Materials.Electrochemical tests were performed using a Gr anode and a Li1.03(Ni0.5Co0.2Mn0.3)0.97O2 (NCM523)cathode.Theanode contained 91.8 wt% graphite (CGP-A12, Philips 66), 2 wt% of carbon black (C45, Timcal), 0.2 wt% oxalic acid and 6 wt% poly(vinylidene difluoride) (PVdF) binder (KF-9300, Kureha). The cathode contained 90 wt% NCM523 (Toda) and 5 wt% of both C45 and PVdF (Solvay 5130). Slurries were coated on battery grade copper and aluminum foils, respectively. ...

**5. `10.1149/1945-7111/ab8c84::chunk::0040`**

SOC = 74.1% using the semi-optimal protocol is even higher than 10C CCCV, which has a large driving force for lithium plating (Fig. 3). Novel Charging Protocols Without Lithium Plating In summary, a LIB should not be exposed to high current and high voltage at the same time to avoid lithium plating. To achieve fast charging without plating, the cell should be charged at a higher rate when the cell voltage is low, and charged to a higher voltage when the charge rate is low. The suppression of lithium plating with the semi-optimal protocol will also increase the cycle life of a cell. While the exact improvement in lifetime needs to be measured experimentally, an estimate is made based on av...

**6. `10.1149/1945-7111/aba550::chunk::0014`**

phase lithium plating conditions should be achieved. After CC-charge phase a relaxation phase of 2 h has been allowed followed by 1/3 C discharge to 0% SoC. Experimental After each CC-charge test and following discharge a capacity check has been performed. In this check the cell was fully charged with 1/3 C followed by a constant voltage (short: CV) phase and after a suf fi cient relaxation time also discharged with 1/3 C to 0%SoC without CV phase. For all tested conditions in the test case two, new cells were used to eliminate the in fl uence of cell ageing due to lithium plating condition in the test before. Figure 1. Test setup layout for constrained li-ion cell measurement. The third ...

**7. `10.1149/1945-7111/abd607::chunk::0051`**

ions out of the plated lithium. - Experimental veri fi cation of the protocol in BIL test station. - Reduction of charging time and extension of cycle life. Table III. Charging times up to 100% SOC at different cycle numbers. Compared with 2C CC/CV charging, the charging time is reduced 32% and 25% up to 80% and 100% SOC, respectively and the degradation becomes less after 160 cycles. Future work will include optimization of the fast charging protocol considering the temperature effects and cooling power of battery pack. Appendix A: List of Model Parameters (a: Manufacturers; b: Tuning with the Model; c: Literature)

**8. `10.1149/1945-7111/abd609::chunk::0003`**

sealed battery test cell! For precise long-term measurements of solid-state cell chemistries Learn more on our product website: Download the data sheet (PDF): You may also like Half cell SiC480 + LPSCI vs. In/lnLi Coulombic efficiency / % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com

**9. `10.1149/1945-7111/abd609::chunk::0005`**

accounts for these observations and provides a means to extrapolate the approach to other cell designs and operation regimes, drawing the maximum average fast charging rates that can still avoid Li plating. Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating © 2021 The Author(s). Published on behalf of The Electrochemical Society by IOP Publishing Limited. This is an open access article distributed under the terms of the Creative Commons Attribution 4.0 License (CC BY, http://creativecommons.org/licenses/ by/4.0/), which permits unrestricted reuse of the work in any medium, provided the original work is properly cited. [DOI: 10.1149/ 1945-7111/...

**10. `10.1149/1945-7111/abb70d::chunk::0043`**

migration in the LiCx electrode accelerates significantly at high rates when the graphite lattice becomes strained. It was impossible to model the fast charge regimes without taking this effect into account. Results and Discussion Figures 14a and 14b present simulations of the ' safe lines ' in Figures 10a and 10b. Using the model, we calculated the ' safe line ' for the anode surface potential η a which is not accessible experimentally. As seen from the plot, due to potential drop across the electrolyte- fi lled separator, the difference between the crossing currents corresponding to these anode potentials systematically increases with the current rate. The overall shape of these ' safe ...

**11. `10.1149/1945-7111/abb70d::chunk::0045`**

on the graphite anode) with lower C-rates, thinner electrodes, and higher temperatures (see Fig. 12). For a 70 μ m thick electrode, full cell capacity can Conclusions Figure 14. A numerical simulation of the ' safe lines ' shown in Fig. 10 plotted over an extended range in both axes. The crossing (a) times and (b) lithiation x transferred by a rectangular pulse applied at 3.57 V are plotted vs the charge C-rate ( the vertical axis ). The empty and fi lled symbols are for the anode reference and surface potentials, respectively, for 30 °C ( circles ) and 45 °C ( squares ). The difference between the two potentials increases with the C-rate. For a fi xed time/ lithiation, the C-rates below ...

**12. `10.1149/2.0401906jes::chunk::0012`**

offset can be minimized by using a highly conductive electrolyte and further reduced by placing the RE very close to the electrode (e.g., by using a Luggin capillary). 4 Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials There is a vast literature on cell configurations for 3-electrode tests in Li-ion batteries, mostly in the context of electrochemical impedance spectroscopy (EIS). 11,16-20 As the a.c. currents are low, the EIS experimental designs are flexible, and artifacts arising from improperly constructed REs are easily identifiable. Validating electrode potentials for Li-ion cells operated in realistic d.c. current regim...

**13. `10.1149/2.0401906jes::chunk::0014`**

at 120°C for 12 h before cell assembly. The cells contained 1.6 mL of liquid electrolyte, which exceeds the combined pore volumes of the electrodes and separators. Experimental Most of the tests used a 1.2 mol/dm 3 lithium hexafluorophosphate (LiPF6) in a 3:7 wt/wt mixture of ethylene and ethyl methyl carbonates ('Gen2,' Tomiyama) as electrolyte. In some experiments, 0.7 M of lithium bis(oxalate)borate (LiBOB) was used as the electrolyte salt instead of 1.2 M LiPF6. In the following narrative, these cells are referred to as LiPF6 and LiBOB cells, respectively.

**14. `10.1149/1945-7111/ab8c84::chunk::0039`**

larger due to the limited time spent in the initial CC charging. For a given initial C rate, the charging protocol with a lower V buffer will have a higher charge acceptance. Novel Charging Protocols Without Lithium Plating Without lithium plating ( V buffer = 0), the simulated semi-optimal protocol can charge the cell to SOC = 74.1% in 10 min, which is ∼ 12% higher than that of CCCV. It should be noted that the achieved charge acceptance of SOC = 74.1% using the semi-optimal protocol is even higher than 10C CCCV, which has a large driving force for lithium plating (Fig. 3).

**15. `10.1149/1945-7111/ab8c84::chunk::0041`**

With 8% loss of active NMC and 7% loss of lithium inventory, the expected capacity fade from running the model with decreased available lithium and NMC is around 6%. Novel Charging Protocols Without Lithium Plating Thus, the proposed protocol is expected to decrease capacity fade from 20% -40% to around 6% in 450 cycles. Figure 8. Variation of min( f f -s e ) versus cell state-of-charge after 10 min charging using the semioptimal protocol. The colorbar of the symbols re fl ect the mean cell temperature during the charging process. While the semi-optimal charging protocol investigated in this subsection can signi fi cantly improve the no-plating charging capacity in 10 min and potentially ...

---
