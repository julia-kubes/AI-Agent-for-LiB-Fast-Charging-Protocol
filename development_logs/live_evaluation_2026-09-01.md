# Five-query live RAG evaluation

- Generated: 2026-09-01T16:28:02.740755+00:00
- Mode: `live`
- Model: `gpt-5.4-mini`
- Query count: 5
- Purpose: diagnose retrieval relevance, protocol specificity, analogue transfer, and appropriate refusal.

The query text is reproduced exactly at the start of each section. Evidence excerpts are diagnostic context, not complete papers.

## Query 1: Broad mechanism and strategy search

### Exact query

> What fast-charging strategies reduce lithium plating in graphite-anode lithium-ion cells?

### Intended test

Whether broad retrieval finds relevant mechanisms and actionable strategies without target-cell details.

### Supplied operating conditions

*(None.)*

### Execution and validation

- Validation: `pass`
- Warnings: 0
- Agent rounds: 3
- Tool calls: 7
- JSON repair attempts: 0
- Input tokens: 6833
- Output tokens: 1511
- Total tokens: 8344
- Elapsed seconds: 93.68
- Retrieved chunks retained: 11
- Distinct papers retained: 5

### Generated answer

The literature evidence points to a few recurring fast-charging strategies that reduce lithium plating in graphite-anode Li-ion cells: raise cell temperature during charge within studied ranges, use variable-rate or pulse-based charging guided by anode-potential limits, and reduce transport limitations through cell design choices such as thinner graphite electrodes. The strongest direct evidence here comes from Argonne studies using reference electrodes and model-based ‘safe lines’ for avoiding zero anode potential, plus a review noting that lower tortuosity and avoiding local salt depletion can reduce plating risk. However, the evidence is cell-specific and does not validate any protocol for deployment.

#### Protocol suggestions

**1. Use temperature-aware fast charging, including rapid preheating before charge and avoiding prolonged exposure to very high temperatures**

- Origin: `reported`
- Confidence: `high`
- Rationale: The papers report that higher temperature generally lowers polarization and can mitigate lithium plating, and that rapid preheating followed by discharge at ambient temperature has been shown to suppress plating and extend cycle life. They also report that benefits can reverse above about 45 °C because cathode-side resistance and degradation grow, so temperature must be managed rather than simply maximized.
- Applicable conditions: Graphite-anode Li-ion cells studied at elevated temperatures; Protocols where plating risk is the main constraint and thermal management is available
- Limitations: Exact temperature setpoints and dwell times are not provided in the evidence summary here.; The favorable temperature window is cell- and design-dependent.; Higher temperature can accelerate other degradation modes, so this is not a universal solution.
- Evidence chunks: `soc_2020::chunk::0008`, `soc_2020::chunk::0044`, `soc_2020::chunk::0045`

**2. Use variable-rate charging controlled by anode potential, with current tapering or pulse sequences chosen to keep anode potential above the lithium-plating threshold**

- Origin: `reported`
- Confidence: `high`
- Rationale: Argonne Part V reports a variable-rate anode-potential charging protocol using a reference electrode to continuously monitor and adjust current, avoiding low anode potentials that favor Li deposition. Part IV reports ‘safe lines’ derived from experiment and model that can be used to prescribe pulse sequences avoiding lithium plating while maintaining average charge rates well above 4C. The review also notes that non-uniform SOC and transport limitations increase plating risk, which supports tapering or pulsing to manage local overpotential.
- Applicable conditions: Cells where anode potential can be monitored directly or estimated reliably; Fast-charge protocols that can be optimized offline or via model-based control
- Limitations: The exact pulse amplitudes, frequencies, and taper shapes are not specified in the retrieved chunks.; These protocols were demonstrated on specific NCM523/graphite or NCM/graphite laboratory cells, not generalized across all graphite-anode cells.; Anode-potential sensing is not always available in practical packs.
- Evidence chunks: `pdf_6fec389acaf110ab::chunk::0004`, `pdf_6fec389acaf110ab::chunk::0005`, `soc_2020::chunk::0043`, `soc_2020::chunk::0044`, `tomaszewska_2019::chunk::0026`

**3. Reduce transport bottlenecks through cell design choices such as thinner graphite electrodes and lower tortuosity, rather than relying only on charge-profile changes**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: The review states that thicker electrodes increase the need to maintain sufficient Li+ concentration at the anode/electrolyte interface, and that reduced pore tortuosity is a key lever to avoid electrolyte transport limitations and the resulting overpotential increase. Argonne Part IV also reports that, for constant-current charging, higher capacities can be safely attained with thinner electrodes and higher temperatures. Together, these findings suggest that design-level transport improvements reduce plating propensity during fast charge.
- Applicable conditions: Cell design stage or when comparing candidate electrodes for fast-charge applications; Graphite anodes where electrolyte transport and local salt depletion are limiting
- Limitations: This is a design strategy, not a standalone charging protocol.; The evidence is qualitative in the retrieved chunks and does not provide a universal electrode-thickness threshold.; Tradeoffs with energy density and manufacturing constraints are not addressed here.
- Evidence chunks: `tomaszewska_2019::chunk::0026`, `soc_2020::chunk::0044`, `soc_2020::chunk::0045`

#### Conflicting evidence

- Higher temperature can reduce plating risk, but the same sources warn that temperatures above about 45 °C can become counter-productive for long-term performance because cathode resistance and other degradation mechanisms increase.
- The review notes that negative anode potential was often assumed to imply plating in some studies, but plating was not always directly confirmed by other methods, so some protocol boundaries are model- or inference-based rather than directly observed.

#### Missing information

- Exact current limits, C-rates, pulse widths, rest times, and voltage cutoffs for a deployable protocol.
- Whether the target cell chemistry, electrode thickness, and thermal design match the studied cells.
- Direct plating diagnostics for the specific cell of interest.
- Pack-level constraints such as balancing, cooling capacity, and sensor availability.

#### Safety notes

- Do not assume a literature-derived fast-charge protocol is validated for deployment.
- Avoid extrapolating temperature or current limits beyond the studied cell designs.
- Protocols that rely on anode-potential feedback or reference electrodes are laboratory methods and may not be practical in production packs.
- Lithium plating risk and thermal degradation must be evaluated together; reducing one can worsen the other.

#### Follow-up questions

- What exact graphite-anode cell chemistry, electrode thickness, and form factor are you targeting?
- Do you want only experimentally demonstrated protocols, or are model-based protocols acceptable?
- Is anode-potential sensing available, or should suggestions be limited to pack-level observables such as voltage and temperature?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 3. Design of optimal fast charging method considering temperature effects | (8,) | 0.9205114841461182 | 0.8072757991060214 | `doi_10.1016_j.jpowsour.2019.03::chunk::0045` |
| 2 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and ' Safe Lines ' to Avoid Lithium Plating | (2,) | 0.9167672395706177 | 0.8220471898855081 | `soc_2020::chunk::0008` |
| 3 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) | 0.9075833559036255 | 0.8100924221626484 | `pdf_6fec389acaf110ab::chunk::0005` |
| 4 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) | 0.9070625901222229 | 0.805999311287112 | `pdf_6fec389acaf110ab::chunk::0004` |
| 5 | Lithium-ion battery fast charging: A review | 2.1. Rate-limiting processes | (4, 5) | 0.901583194732666 | 0.8087570280306282 | `tomaszewska_2019::chunk::0026` |
| 6 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (11,) | 0.9214403629302979 | 0.8308982687178259 | `soc_2020::chunk::0044` |
| 7 | You may also like | Novel Charging Protocols Without Lithium Plating | (8, 9) | 0.9177049398422241 | 0.8053466234728612 | `unknown_2020::chunk::0042` |
| 8 | Lithium-ion battery fast charging: A review | 5.1. Types of charging protocols | (13, 14) | 0.9128388166427612 | 0.8004379842404407 | `tomaszewska_2019::chunk::0078` |
| 9 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Results and Discussion | (11,) |  |  | `soc_2020::chunk::0043` |
| 10 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (12,) |  |  | `soc_2020::chunk::0045` |
| 11 | Lithium-ion battery fast charging: A review | 2.1. Rate-limiting processes | (4, 5) |  |  | `tomaszewska_2019::chunk::0027` |

#### Evidence excerpts

**1. `doi_10.1016_j.jpowsour.2019.03::chunk::0045`**

that can be used for generating a charging protocol I. The temperature is varied according to the curve shown in Fig. 4(b) in order to continuously suppress the degradation. 3. Design of optimal fast charging method considering temperature effects In the second step, the lithium plating is considered and the pulse discharging current is added to the charging protocol I to promote the lithium stripping. The pulse frequency and amplitude are optimized in order to reduce the total discharging capacity while making sure that the plated lithium is completely recovered. In order to optimize the pulse discharging current, the control horizon of NMPC has to be larger than 20, which cannot be fini...

**2. `soc_2020::chunk::0008`**

in Li-ion cells. Our studies are intended to spur development of LIB cells that can be charged at a 6C rate without sacri fi cing safety and durability. Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and ' Safe Lines ' to Avoid Lithium Plating One of the recognized complications in fast charging of LIBs is Li metal plating on the anode, which occurs when the electrode potential becomes so low that this reaction becomes competitive with Li + ion intercalation into the graphite. 10 -13 Charging at higher temperatures can mitigate this plating, but at a price. 14 The higher temperature enhances diffusion in the electrolyte, Li + ion desolvation processes at the electrode, and tr...

**3. `pdf_6fec389acaf110ab::chunk::0005`**

accounts for these observations and provides a means to extrapolate the approach to other cell designs and operation regimes, drawing the maximum average fast charging rates that can still avoid Li plating. Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating © 2021 The Author(s). Published on behalf of The Electrochemical Society by IOP Publishing Limited. This is an open access article distributed under the terms of the Creative Commons Attribution 4.0 License (CC BY, http://creativecommons.org/licenses/ by/4.0/), which permits unrestricted reuse of the work in any medium, provided the original work is properly cited. [DOI: 10.1149/ 1945-7111/...

**4. `pdf_6fec389acaf110ab::chunk::0004`**

/ % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating Ilya A. Shkrob, Marco-Tulio F. Rodrigues, and Daniel P. Abraham * ,z Chemical Sciences and Engineering Division, Argonne National Laboratory, Lemont, Illinois 60439, United States of America ECS Fast charging of Li-ion batteries would make ' fueling ' of electric vehicles comparable in time to fueling of gasoline-powered cars, increasing consumer appeal of the new technology. Taking the US Department of Energy goal of safe 6 C charging to 80% capacity as a guide, we describe approaches that can mitigate Li plati...

**5. `tomaszewska_2019::chunk::0026`**

of their modelling study showed that while both extremely low and extremely high temperatures were generally damaging, fast charging shifted the balance in favour of higher temperatures, particularly for high energy cells. 2.1. Rate-limiting processes While the intersection of phenomena, materials chemistry and component design are described in the following sections, anode thickness and its in fl uence on transport provides a useful lens to explore their linkages. While thin electrodes are generally considered to represent ideal transport [26], when electrodes are suf fi ciently thick, it becomes critical to ensure suf fi cient Li þ concentration at the electrode/electrolyte interface th...

**6. `soc_2020::chunk::0044`**

, and elsewhere we use it to prescribe pulse sequences that avoid LPC while providing an average charge rate, well in excess of 4C, that precludes Li-plating. Conclusions Constant current and pulse current charging were conducted on NCM523/Gr cells containing a Li-metal reference electrode at 30 °C, 37 °C, 45 °C, and 55 °C. By repeating the experiment for many C-rates we mapped the currents at which the anode potential (as measured by the reference electrode) reached or crossed zero vs Li/Li + . We used these maps, and a state-of-the art multiphase electrochemical model, to compute the currents at which anode surface potential reaches zero vs Li/Li + , thereby determining the boundary of ...

**7. `unknown_2020::chunk::0042`**

following subsections, the features learned from the semi-optimal protocol are used to develop feasible fast charging protocols that allow faster charge with lower or no driving force for lithium plating. Novel Charging Protocols Without Lithium Plating Constant-current charging followed by voltage ramping. -It can be seen from Fig. 7a that the semi-optimal charging protocol is composed of multiple constant-current steps with different durations. It would be dif fi cult to implement such charging protocol in terms of charge current, as it requires two parameters for each step (C rate, duration time or cutoff voltage), which rapidly becomes intractable when the number of steps increases. H...

**8. `tomaszewska_2019::chunk::0078`**

shown to achieve reduced charging times, increased ef fi ciencies and/or improved capacity or power retention. Fig. 8 illustrates some of the alternative protocols proposed for fast charging. 5.1. Types of charging protocols Zhang et al. [192] studied the effects of the CC-CV charging protocol on the reversible capacity and anode potential evolution in experimental LCO/graphite cells with embedded reference electrodes as they were charged at ambient temperatures from -20 + C to 10 + C with C-rates between 0.16C and 1.2C. The results showed a positive correlation between increasing charging current in the CC phase and increasing time taken by the CV phase to complete. The authors observed ...

**9. `soc_2020::chunk::0043`**

migration in the LiCx electrode accelerates significantly at high rates when the graphite lattice becomes strained. It was impossible to model the fast charge regimes without taking this effect into account. Results and Discussion Figures 14a and 14b present simulations of the ' safe lines ' in Figures 10a and 10b. Using the model, we calculated the ' safe line ' for the anode surface potential η a which is not accessible experimentally. As seen from the plot, due to potential drop across the electrolyte- fi lled separator, the difference between the crossing currents corresponding to these anode potentials systematically increases with the current rate. The overall shape of these ' safe ...

**10. `soc_2020::chunk::0045`**

on the graphite anode) with lower C-rates, thinner electrodes, and higher temperatures (see Fig. 12). For a 70 μ m thick electrode, full cell capacity can Conclusions Figure 14. A numerical simulation of the ' safe lines ' shown in Fig. 10 plotted over an extended range in both axes. The crossing (a) times and (b) lithiation x transferred by a rectangular pulse applied at 3.57 V are plotted vs the charge C-rate ( the vertical axis ). The empty and fi lled symbols are for the anode reference and surface potentials, respectively, for 30 °C ( circles ) and 45 °C ( squares ). The difference between the two potentials increases with the C-rate. For a fi xed time/ lithiation, the C-rates below ...

**11. `tomaszewska_2019::chunk::0027`**

, inducing the formation of dendritic structures in place of the more uniform mossy deposits formed when suf fi cient amounts of lithium are available in the electrolyte [29,38]. 2.1. Rate-limiting processes To avoid the phenomena that result in plating or dendrite growth, Gallagher et al. recommended operating at current densities below 4 mA cm -2 but acknowledged the complex interactions of operating parameters in providing such guidelines [17]. Due to the difference in mass loadings and other characteristics between cells, the general applicability of this recommendation may be questioned. Alternative anode materials are also the subject of signi fi cant research, to assist in addressi...

---

## Additional manual UI evaluation: Pulse charging for an ambiguously identified Tesla

### Test provenance

- Source: Manual Streamlit test supplied by the user
- Automated execution statistics: Not captured
- Purpose: Evaluate handling of an ambiguous or possibly incorrect vehicle model,
  lack of pack specifications, pulse-charging evidence, and safety boundaries.

### Exact query

> Give me a pulse charging protocol for my 2020 tesla model 5.

### Full copied response

#### Fast-Charging Literature Assistant Response

##### Summary

I could not find evidence specific to a 2020 Tesla Model 5, and the retrieved literature is mostly on generic lithium-ion cells or EV-relevant NCA/NMC cells rather than Tesla pack-level protocols. The papers support only general pulse-charging concepts: pulse/rest can reduce polarization or lithium-plating risk in some cells, but other work reports pulse charging can be no better than comparable fast-charging CCCV and may lower efficiency or accelerate degradation. Because your operating conditions are empty, I cannot responsibly specify current, voltage, temperature, SOC window, or timing for a vehicle protocol.

##### Protocol suggestions

###### 1. Use a conservative pulse-rest fast-charge concept only as a research starting point: short charge pulses separated by rest periods, with the pulse intensity reduced as charge progresses.

One study reports that pulse charging with varying currents and rest pulses can keep surface lithium concentration near saturation while preventing surface saturation, and another reports that current interrupts/reverses every 10 s for 1 s can reduce concentration polarization and may strip minor Li-plating seeds. However, these are cell-specific research results, not a validated Tesla protocol.

- Origin: synthesized
- Confidence: low
- Applicable conditions: Generic Li-ion cells where pulse charging is being explored; Situations where polarization or lithium plating is the main concern
- Limitations: No Tesla-specific validation; No operating current, voltage, temperature, or SOC limits provided in the evidence; Reported benefits depend strongly on cell chemistry and test conditions
- Evidence chunks: doi_10.1149_2.0871507jes::chunk::0031, doi_10.1016_j.jpowsour.2014.07.106::chunk::0025, doi_10.1149_1945-7111_a08c3b1a::chunk::0043

###### 2. If the goal is minimizing lithium plating risk, favor lower current near the end of charge rather than aggressive pulses throughout the whole charge.

Multiple sources indicate that plating risk rises at high charge rates and near the end of charge, and that smaller current near the end can reduce negative phenomena. One NCA study also notes that controlling gas evolution and phase transition from 0% to 40% SOC is important, implying that protocol design should be SOC-dependent rather than fixed.

- Origin: synthesized
- Confidence: medium
- Applicable conditions: Cells where end-of-charge plating risk is the dominant constraint; High-SOC charging region
- Limitations: This is a synthesis across studies, not a directly reported Tesla protocol; The evidence does not provide a universal pulse schedule; The SOC ranges and temperatures are cell-specific and not transferable without testing
- Evidence chunks: doi_10.1002_est2.141::chunk::0017, doi_10.1002_est2.141::chunk::0049, soc_2020::chunk::0044

###### 3. Do not assume pulse charging is superior to CCCV; compare against a conventional fast-charge baseline before adopting it.

A review-style source states that pulse charging and boost charging may have similar charge speeds to comparable fast-charging CCCV, and that pulse charging can have lower charge efficiency. Another study found pulse charging improved cycling in one commercial cell, showing the literature is mixed and chemistry-dependent.

- Origin: reported
- Confidence: medium
- Applicable conditions: Any lithium-ion fast-charging evaluation
- Limitations: Conflicting results across chemistries and test setups; No evidence here establishes superiority for Tesla cells; No deployment validation
- Evidence chunks: unknown_2020::chunk::0011, li_2001::chunk::0008

##### Conflicting evidence

- Some studies report pulse charging can reduce charge time, improve cycling, or reduce degradation in specific cells, while other literature says pulse charging may have similar speed to fast-charging CCCV, lower efficiency, or even accelerate degradation. The evidence is therefore mixed and strongly cell-dependent.
- The retrieved evidence includes both charge-pulse and pulse-discharge variants; these are not interchangeable, so results from one cannot be directly applied to the other.

##### Missing information

- Exact Tesla model and battery chemistry
- Pack or cell-level charging objective
- Allowed charging source and charger capabilities
- Starting SOC, target SOC, ambient and battery temperature
- Maximum allowable current, voltage, and power
- Whether the goal is speed, cycle life, low-temperature charging, or plating avoidance
- Whether you want a pack-level recommendation or a cell-research protocol

##### Safety notes

- I cannot provide a deployable charging protocol for a vehicle from this evidence.
- Do not apply literature pulse schedules directly to a Tesla pack without manufacturer guidance and validation.
- Pulse charging can increase temperature and may worsen degradation or efficiency depending on chemistry and conditions.
- If the battery is cold or near high SOC, charging risk can increase; the literature suggests these regions need special caution.

##### Follow-up questions

- Do you mean a 2020 Tesla Model 3, Model Y, or another model?
- What is the battery chemistry or pack type, if known?
- What is your goal: fastest charge, longest life, cold-weather charging, or reduced lithium plating risk?
- What starting SOC, target SOC, and battery temperature range should the protocol cover?
- Are you asking for a research summary or a manufacturer-safe charging recommendation?

---

## Query 2: Specific NMC811 pouch-cell target

### Exact query

> Propose an evidence-supported starting fast-charge protocol for a 5 Ah graphite/NMC811 pouch cell at 25 °C, charging from 10% to 80% SOC with a target time of 20 minutes while limiting lithium plating. Give current stages and transition criteria only when supported, and clearly identify values that cannot be determined from the evidence.

### Intended test

Whether detailed target conditions produce a more concrete protocol and whether unsupported numerical specificity is withheld.

### Supplied operating conditions

- chemistry: graphite/NMC811
- form_factor: 5 Ah pouch cell
- temperature: 25 °C
- soc_range: 10-80%
- objective: target 20 minutes while limiting lithium plating

### Execution and validation

- Validation: `pass`
- Warnings: 0
- Agent rounds: 3
- Tool calls: 7
- JSON repair attempts: 0
- Input tokens: 7546
- Output tokens: 1800
- Total tokens: 9346
- Elapsed seconds: 45.29
- Retrieved chunks retained: 14
- Distinct papers retained: 6

### Generated answer

Evidence supports only a cautious starting point, not a validated protocol, for a graphite/NMC811 pouch cell at 25 °C from 10% to 80% SOC. The closest directly reported fast-charge results are for graphite/NMC or graphite/NMC532 pouch cells, not NMC811, and they show that lithium-plating-limited fast charging is achieved by reducing current in stages before plating onset or by using current maps tied to anode-potential/plating indicators. A 15–15.5 min charge to 80% SOC was reported for larger pouch cells under specific conditions, but the exact current schedule is not transferable from the evidence to this 5 Ah NMC811 cell.

#### Protocol suggestions

**1. Use a staged constant-current protocol that starts with a higher current at low SOC and steps down before lithium-deposition onset, with transition criteria based on a plating indicator rather than fixed SOC alone.**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: One study reports that the charging current in a stepwise protocol is reduced to the next lower current before lithium deposition onset is reached, using pressure and temperature signatures to detect onset at 25 °C; another reports that fast charging without plating is favored when the cell is charged at higher rate when voltage is low and at higher voltage only when current is low. This supports a staged approach, but not exact current values for NMC811.
- Applicable conditions: graphite-based pouch cells at 25 °C; 10% to 80% SOC fast charge objective; lithium-plating avoidance prioritized
- Limitations: No exact current magnitudes for a 5 Ah graphite/NMC811 pouch cell are provided.; Transition criteria in the evidence rely on measured onset of lithium deposition or model-derived anode potential, not a simple universal SOC threshold.; The reported protocol was validated on different chemistries/form factors than the user’s cell.
- Evidence chunks: `doi_10.1149_1945-7111::chunk::0048`, `doi_10.1149_1945-7111::chunk::0049`, `unknown_2020::chunk::0040`, `unknown_2020::chunk::0041`

**2. If a voltage-limited stage is used, keep the high-current stage from extending into the high-voltage region where plating driving force rises; then taper current as voltage rises.**

- Origin: `synthesized`
- Confidence: `low`
- Rationale: The literature indicates that CCCV/CPCV outperform simpler multistage constant-current charging in terms of maximum driving force for lithium plating, and that to avoid plating the cell should be charged at higher current when voltage is low and at higher voltage only when current is low. This supports a protocol that avoids simultaneous high current and high voltage.
- Applicable conditions: graphite/NMC pouch cells; 25 °C; fast charge with plating limitation
- Limitations: The evidence does not provide a transferable voltage cutoff for NMC811 at 25 °C.; The cited cutoff of 4.1 V was reported for a modeled graphite/NMC532 cell with a specific loading, so it cannot be assumed for this cell.; No direct evidence here establishes that CCCV is optimal for the requested 20 min target.
- Evidence chunks: `unknown_2020::chunk::0066`, `unknown_2020::chunk::0040`

**3. Use the literature only as a starting envelope: a 10% to 80% SOC charge in about 15 to 15.5 minutes has been demonstrated for larger pouch cells under specific conditions, but for this 5 Ah NMC811 cell the evidence is insufficient to specify a safe current schedule that reliably meets 20 minutes.**

- Origin: `reported`
- Confidence: `low`
- Rationale: One paper reports 80% nominal capacity charged in 15.5 min at battery-pack level and about 15 min at pouch-cell level under its own setup; another reports 0% to 85% SOC in 26.8 min at 25 °C using a stepwise protocol. These results show the target time is plausible in the literature, but the exact protocol depends on cell design and sensing method.
- Applicable conditions: pouch-cell fast charging benchmark context; 25 °C in some reported tests; 80% SOC endpoint
- Limitations: The 15–15.5 min result was for a different, larger pouch cell and cannot be directly scaled to 5 Ah NMC811.; The 26.8 min result was for a different cell and SOC window (0% to 85%), so it does not directly satisfy the requested 10% to 80% window.; No evidence here provides a validated 20-minute protocol for NMC811.
- Evidence chunks: `doi_10.1016_j.jpowsour.2019.04.047::chunk::0061`, `doi_10.1016_j.jpowsour.2019.04.047::chunk::0062`, `doi_10.1149_1945-7111::chunk::0049`

#### Conflicting evidence

- A 15–15.5 min charge to 80% capacity is reported for a larger pouch-cell system, but a different study reports 0% to 85% SOC in 26.8 min at 25 °C; these are not directly comparable because the cells, sensing methods, and charge windows differ.
- One source suggests CCCV/CPCV outperform multistage constant-current charging for plating driving force, while another demonstrates a stepwise current-reduction protocol based on deposition onset; the evidence does not establish a single best protocol for the user’s NMC811 cell.

#### Missing information

- Exact NMC811 cell design details: electrode loadings, N:P ratio, thicknesses, electrolyte, separator, tab geometry, and thermal boundary conditions.
- A transferable current-vs-SOC or voltage-vs-current map for this specific 5 Ah graphite/NMC811 pouch cell at 25 °C.
- A validated plating-onset criterion for this cell, such as anode potential vs Li/Li+ or a measurable proxy tied to this exact design.
- Whether the 20-minute target is measured from 10% SOC to 80% SOC under rest-free charging or includes any dwell/relaxation time.
- Any manufacturer limits for maximum charge current, voltage ceiling, or temperature rise.

#### Safety notes

- Do not assume the literature-derived current levels or voltage cutoffs are safe for this specific cell.
- Lithium plating risk increases when high current and high voltage occur together; the evidence supports reducing current before plating onset rather than relying on SOC alone.
- Because the evidence is not specific to NMC811, any starting protocol should be treated as exploratory and experimentally re-validated with plating diagnostics before deployment.

#### Follow-up questions

- What are the cell’s exact voltage limits, electrode loadings, N:P ratio, and thicknesses?
- Can you provide an anode-potential reference or a plating-sensing method for this cell?
- Is the 20-minute target strict, or can a slightly longer charge time be accepted to reduce plating risk?
- Do you want a protocol optimized for minimum plating risk, minimum time, or a compromise between the two?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | You may also like | Conclusions | (13,) | 0.8562949895858765 | 0.7779557024239832 | `unknown_2020::chunk::0066` |
| 2 | Extreme Fast Charge Challenges for Lithium-ion Battery: Variability and Positive Electrode Issues | Experimental | (5,) | 0.8532972931861877 | 0.7771100771608246 | `tanim_2015::chunk::0008` |
| 3 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (11,) | 0.8496696352958679 | 0.7837452201871812 | `soc_2020::chunk::0044` |
| 4 | Non-destructive fast charging algorithm of lithium-ion batteries based on the control-oriented electrochemical model | 4. Applying the fast charging algorithm to a commercial lithium-ion battery: experimental validation | (6, 7) | 0.8431872725486755 | 0.772045115999188 | `pdf_e648a41cdcfc30f1::chunk::0032` |
| 5 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 5. Conclusions and future work | (9, 10) | 0.8430158495903015 | 0.7928102632651945 | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0062` |
| 6 | You may also like | Results and Discussion | (11,) | 0.9086579084396362 | 0.8083563096365286 | `doi_10.1149_1945-7111::chunk::0049` |
| 7 | You may also like | Novel Charging Protocols Without Lithium Plating | (8,) | 0.8883144855499268 | 0.8060983662820428 | `unknown_2020::chunk::0040` |
| 8 | You may also like | Results and Discussion | (11,) |  |  | `doi_10.1149_1945-7111::chunk::0048` |
| 9 | You may also like | Results and Discussion | (11,) |  |  | `doi_10.1149_1945-7111::chunk::0050` |
| 10 | You may also like | Novel Charging Protocols Without Lithium Plating | (8,) |  |  | `unknown_2020::chunk::0039` |
| 11 | You may also like | Novel Charging Protocols Without Lithium Plating | (8,) |  |  | `unknown_2020::chunk::0041` |
| 12 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.3. Battery pack level | (9,) |  |  | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0061` |
| 13 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | Acknowledgements | (10,) |  |  | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0063` |
| 14 | Extreme Fast Charge Challenges for Lithium-ion Battery: Variability and Positive Electrode Issues | Experimental | (5, 6) |  |  | `tanim_2015::chunk::0009` |

#### Evidence excerpts

**1. `unknown_2020::chunk::0066`**

ing protocol. However, several CCCV steps are likely needed as the higher loading cell is more prone to lithium plating, increasing implementation complexity compared to the voltage ramping protocol. Conclusions In this work, the Pseudo2D electrochemical battery model was used to screen traditional fast charging protocols for a moderate HEV loading (2.5 mAh cm -2 ) graphite/NMC 532 cell. The simulation results showed that in terms of the maximum driving force for lithium plating, CCCV and CPCV protocols outperform the multistage constant-current charging with a single voltage cutoff and the pulse charging. To prevent lithium plating, the 5C + constant-current charging stage should be term...

**2. `tanim_2015::chunk::0008`**

charging. These issues are often overlooked due to the focus on Li metal plating during fast charging, but have the potential to significantly impact the eventual application and use of fast charging. Experimental Table I lists the material, electrode, cell design parameters, and Table II includes the charging protocols. Graphite (1506T Superior Graphite) and NMC532 (Toda America) were used as respective negative and positive electrode active materials, respectively, to fabricate electrodes at the Cell Analysis, Modeling, and Prototyping (CAMP) Facility at Argonne National Laboratory (Argonne). These electrodes were cut and assembled in single layer pouch cells with Celgard 2320 separator...

**3. `soc_2020::chunk::0044`**

, and elsewhere we use it to prescribe pulse sequences that avoid LPC while providing an average charge rate, well in excess of 4C, that precludes Li-plating. Conclusions Constant current and pulse current charging were conducted on NCM523/Gr cells containing a Li-metal reference electrode at 30 °C, 37 °C, 45 °C, and 55 °C. By repeating the experiment for many C-rates we mapped the currents at which the anode potential (as measured by the reference electrode) reached or crossed zero vs Li/Li + . We used these maps, and a state-of-the art multiphase electrochemical model, to compute the currents at which anode surface potential reaches zero vs Li/Li + , thereby determining the boundary of ...

**4. `pdf_e648a41cdcfc30f1::chunk::0032`**

Fig. 5. Profiles of charging from different initial OCV: (a)-(c) 3.73 V, (d)-(f) 3.86 V. 4. Applying the fast charging algorithm to a commercial lithium-ion battery: experimental validation The test results obtained by applying the fast charging algorithm to a large-format commercial lithium-ion battery with an incorporated reference electrode are presented in this section. The commercial pouch cells consisted of NCM/graphite electrodes. The nominal capacity was 40 A h, and the voltage range was 2.84.2 V. To construct a three-electrode cell, the oxidation was removed from a 25l m-diameter copper wire by acid washing, and the wire was then placed on the surface of the anode/separator inter...

**5. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0062`**

constant and heat is barely dissipated. Therefore, the thermal behavior of the battery pack is best emulated at pouch cell level by test setup A using the mechanical setup 1. 5. Conclusions and future work A new fast charging method has been proposed based on a charging current map determined with three-electrode test cells and current control in dependency of the negative electrode potential to avoid lithium plating. The current map was successfully transferred to pouch cell and battery pack level and similar charging times of about 15min were achieved until 80% of the nominal capacity were charged into the cells. Cycle life tests showed that the inhomogeneous current density in a large-...

**6. `doi_10.1149_1945-7111::chunk::0049`**

the stepwise protocol is reduced to the next lower current before lithium deposition onset is reached. The resulting fast charging protocol based on onset of lithium deposition is shown in Table II. Results and Discussion The shown fast charge protocol allows a charging of the cell from 0%SoC to 85%SoC in 26.8 min. To validate the developed charging protocol three cells were cycled with this protocol. Start condition was 25 °C ±1 °C cell temperature and the temperature of the chamber held constant. Cells were cycled in the already presented test setup (refer to Fig. 1) to realize the same test conditions as in second test case. The cycling was started at 0%SoC and the cell was charged wit...

**7. `unknown_2020::chunk::0040`**

SOC = 74.1% using the semi-optimal protocol is even higher than 10C CCCV, which has a large driving force for lithium plating (Fig. 3). Novel Charging Protocols Without Lithium Plating In summary, a LIB should not be exposed to high current and high voltage at the same time to avoid lithium plating. To achieve fast charging without plating, the cell should be charged at a higher rate when the cell voltage is low, and charged to a higher voltage when the charge rate is low. The suppression of lithium plating with the semi-optimal protocol will also increase the cycle life of a cell. While the exact improvement in lifetime needs to be measured experimentally, an estimate is made based on av...

**8. `doi_10.1149_1945-7111::chunk::0048`**

rate = 1.5 C. 70.1% to 85%, C-rate = 1 C. Average 0% - 85%, C-rate = 1.92 C Results and Discussion The same approach has been performed with test results of voltage, pressure and temperature of CC-charge tests. The basic boundary condition was a start temperature of 25 °C and a stepwise charging protocol concept. Basis of developing the fast charge protocol was the calculated onset point of lithium deposition, which was measured during CC-charge based on pressure and temperature. As described before to calculate the onset point, fi rst derivation of pressure trend was calculated to detect the rising gradient and second derivation of temperature measurement was calculated to detect the in ...

**9. `doi_10.1149_1945-7111::chunk::0050`**

comparison to 100 fast charge cycles has been done. Based on the comparison of capacity retention after 100cycles from both tests no abnormal capacity loss based on fast charging could be shown. Results and Discussion These results show that measurement of lithium deposition onset in constrained condition based on pressure and temperature measurement works. The results con fi rm and complement the developed method based on dilatometry measurement in the work of Spingler et al. to determine an optimized fast charge protocol for lithium ion pouch cells. 14 Both measurements are usable possibilities to optimize cell application under different boundary conditions.

**10. `unknown_2020::chunk::0039`**

larger due to the limited time spent in the initial CC charging. For a given initial C rate, the charging protocol with a lower V buffer will have a higher charge acceptance. Novel Charging Protocols Without Lithium Plating Without lithium plating ( V buffer = 0), the simulated semi-optimal protocol can charge the cell to SOC = 74.1% in 10 min, which is ∼ 12% higher than that of CCCV. It should be noted that the achieved charge acceptance of SOC = 74.1% using the semi-optimal protocol is even higher than 10C CCCV, which has a large driving force for lithium plating (Fig. 3).

**11. `unknown_2020::chunk::0041`**

With 8% loss of active NMC and 7% loss of lithium inventory, the expected capacity fade from running the model with decreased available lithium and NMC is around 6%. Novel Charging Protocols Without Lithium Plating Thus, the proposed protocol is expected to decrease capacity fade from 20% -40% to around 6% in 450 cycles. Figure 8. Variation of min( f f -s e ) versus cell state-of-charge after 10 min charging using the semioptimal protocol. The colorbar of the symbols re fl ect the mean cell temperature during the charging process. While the semi-optimal charging protocol investigated in this subsection can signi fi cantly improve the no-plating charging capacity in 10 min and potentially ...

**12. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0061`**

at the end of the test and the cell SetC.2 is still charged faster by around one sixth, as can be seen in Table S2 and Table S3. 4.3. Battery pack level The test at battery pack level is conducted to verify the assumptions made at pouch cell level regarding the heating of the cells and the achievable charging time. The current, voltage and temperature curves are presented in Fig. 8. At battery pack level 80% of the nominal capacity is charged in 15.5min starting at a temperature of 20°C with deactivated cooling circuit. Therefore, despite the reduced starting temperature a similar charging time is attained compared to test setup A at pouch cell level. After 18min the maximum battery pack ...

**13. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0063`**

future work, this approach will be tested at battery pack level over lifetime. Whether or not this approach can be generalized to other cell types with a graphite anode is under investigation. Acknowledgements Our thanks go to Harald Brazel at Zentrum für Sonnenenergie-und Wassersto ff -Forschung Baden-Württemberg (ZSW) for executing the testing of the battery pack in their facilities. Also we thank our colleagues Barbara Seling, Thassilo Knapp and Thomas Deutschen for their support in the material and cell laboratory of Daimler AG in Kirchheim unter Teck. This work was funded by Daimler AG and Deutsche Accumotive GmbH & Co. KG.

**14. `tanim_2015::chunk::0009`**

oversize accommodates slight imperfections of electrode alignment during cell assembly and avoid preferential plating of Li at the edges by guaranteeing there is Gr material directly opposite of the cathode. Experimental 32,33 Single-sided electrodes were used in an xx3450 pouch cell format with an active area of 14.1 cm² for the positive electrode and 14.9 cm² for the negative electrode. Twenty-one cells were assembled in a dry room and formed at CAMP prior to shipment to Idaho National Laboratory (INL) for life and performance evaluation and failure mode analysis. Upon receipt, mass, open circuit voltage (OCV), and high frequency impedance of the cells were measured. Supplemental Figs. ...

---

## Query 3: Known NCM523 evidence target

### Exact query

> Using retrieved experimental evidence, describe a starting fast-charge protocol design for an NCM523/graphite laboratory cell at 30 °C over 0-80% SOC that is intended to avoid lithium plating. Distinguish directly reported protocol elements from synthesis and inference.

### Intended test

Whether retrieval recovers the known Part V protocol paper and whether the answer accurately uses its experimental conditions.

### Supplied operating conditions

- chemistry: NCM523/graphite
- form_factor: laboratory cell
- temperature: 30 °C
- soc_range: 0-80%
- objective: avoid lithium plating

### Execution and validation

- Validation: `pass`
- Warnings: 0
- Agent rounds: 3
- Tool calls: 7
- JSON repair attempts: 0
- Input tokens: 8883
- Output tokens: 1812
- Total tokens: 10695
- Elapsed seconds: 45.62
- Retrieved chunks retained: 17
- Distinct papers retained: 6

### Generated answer

Retrieved experimental evidence for NCM523/graphite fast charging at 30 °C supports a starting design centered on anode-potential-aware control to avoid lithium plating. The strongest directly reported result is that, for charge to 80% capacity at 30 °C, an NCM523/graphite cell with a 70 μm graphite electrode achieved an average 4.97 C, while a 47 μm graphite electrode achieved 7.40 C, using a variable-rate anode-potential charging protocol monitored with a microprobe reference electrode. Related experimental work on NCM523/graphite cells at 30 °C shows that constant-current and pulse-current charging can be mapped to “safe lines” where the anode surface potential remains above 0 vs Li/Li+, and that pulse charging can exceed 4 C average while avoiding plating. However, the literature here does not provide a single validated protocol for your exact cell design over the full 0–80% SOC window, so the suggestions below are a synthesis/inference from those studies rather than a deployment-ready recipe.

#### Protocol suggestions

**1. Use an anode-potential-controlled variable-current charge, with current reduced whenever the monitored anode potential approaches 0 vs Li/Li+; target an average rate near the experimentally reported 4.97 C for a 70 μm graphite electrode at 30 °C as a starting point.**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: The paper on protocols to avoid Li plating reports that a variable-rate anode-potential charging protocol was implemented using a microprobe reference electrode to continuously monitor and adjust current, and that at 30 °C an NCM523/graphite cell with 70 μm graphite electrode reached 80% capacity at an average 4.97 C without reported plating in that demonstration. This supports using anode-potential feedback as the primary design principle.
- Applicable conditions: NCM523/graphite laboratory cell; 30 °C; 0–80% SOC; objective: avoid lithium plating; cell with reference-electrode access or equivalent anode-potential monitoring
- Limitations: The exact current waveform, voltage limits, and anode-potential threshold schedule are not fully specified in the retrieved chunks. The reported 4.97 C is tied to a specific electrode thickness and cell design, so it may not transfer directly to a different laboratory cell.
- Evidence chunks: `pdf_6fec389acaf110ab::chunk::0004`, `pdf_6fec389acaf110ab::chunk::0005`, `pdf_6fec389acaf110ab::chunk::0006`

**2. Design the charge as a pulse-current or piecewise-constant-current sequence constrained by experimentally mapped “safe lines” for 30 °C, keeping each segment below the boundary where the anode surface potential crosses 0 vs Li/Li+.**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: Experimental work on NCM523/Gr cells with a Li-metal reference electrode reports that constant-current and pulse-current charging were mapped at 30 °C, and that the resulting safe lines were used to prescribe pulse sequences that avoid lithium plating while providing an average charge rate well in excess of 4 C. This suggests a practical starting architecture of segmented/pulsed charging rather than a single fixed CC step.
- Applicable conditions: NCM523/graphite laboratory cell; 30 °C; 0–80% SOC; objective: avoid lithium plating; ability to implement pulse or segmented current profiles
- Limitations: The retrieved text does not provide the exact pulse amplitudes, durations, or SOC breakpoints for the safe-line protocol. The evidence is from a specific laboratory cell with a reference electrode, so the safe-line boundary must be re-established for a different cell build.
- Evidence chunks: `soc_2020::chunk::0044`, `soc_2020::chunk::0043`, `soc_2020::chunk::0046`

**3. If temperature control is available, keep the cell at 30 °C and avoid assuming that higher temperature is always beneficial; use temperature only as a fixed condition unless additional cell-specific validation is available.**

- Origin: `reported`
- Confidence: `medium`
- Rationale: The temperature study reports that polarization generally decreases with increasing temperature, but also states that above 45 °C the gains can be offset by growing resistance and that increasing temperature over 45 °C for extended periods is counter-productive for long-term performance. Since your condition is already 30 °C, the evidence supports holding temperature fixed rather than trying to raise it as a plating-avoidance tactic.
- Applicable conditions: NCM523/graphite laboratory cell; 30 °C; 0–80% SOC
- Limitations: This does not by itself define a fast-charge current profile. It only supports temperature as a boundary condition and cautions against extrapolating to higher temperatures without validation.
- Evidence chunks: `soc_2020::chunk::0044`, `soc_2020::chunk::0045`, `soc_2020::chunk::0046`

#### Conflicting evidence

- The 30 °C temperature study indicates that lower temperatures increase plating likelihood and that higher temperatures reduce polarization, but it also warns that temperatures above 45 °C can be counter-productive for long-term performance. Thus, temperature is helpful for plating avoidance only within a limited range, and the literature does not support simply increasing temperature as a universal solution.
- The reported fast-charge rates differ by cell design: 4.97 C average to 80% capacity for a 70 μm graphite electrode versus 7.40 C for a 47 μm graphite electrode at 30 °C. This means the achievable safe rate is strongly design-dependent and not directly transferable.

#### Missing information

- Exact current profile for 0–80% SOC, including segment boundaries, pulse amplitudes, pulse widths, and rest periods.
- Cell-specific anode potential threshold margin below 0 vs Li/Li+ used in the experiments.
- Electrode thickness, areal loading, N:P ratio, separator, electrolyte, and reference-electrode configuration for the user’s exact laboratory cell.
- Whether the user’s cell has a reference electrode or whether the protocol must be inferred from full-cell voltage only.
- Validation data for the exact laboratory cell geometry and materials at 30 °C over repeated cycles.

#### Safety notes

- Do not treat the literature-derived protocol as deployment-validated; it is a research starting point only.
- Avoid any protocol that allows the graphite anode surface potential to cross below 0 vs Li/Li+ if plating avoidance is the objective.
- Because the evidence is cell-design-specific, re-establish safe boundaries experimentally for the exact laboratory cell before use.
- No current, voltage, or timing limit is universally safe to infer from these papers alone.

#### Follow-up questions

- What are the graphite thickness, areal loading, N:P ratio, separator, and electrolyte of the specific NCM523/graphite laboratory cell?
- Does the cell include a reference electrode or other means to estimate anode potential during charge?
- Is the goal to maximize average C-rate, minimize charge time, or maximize cycle life while avoiding plating?
- Can the protocol use pulse charging and/or active temperature control, or must it be a simple CC-CV profile?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | (3,) | 0.9354278445243835 | 0.8355670419903739 | `doi_10.1149_2.0401906jes::chunk::0013` |
| 2 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) | 0.9321773648262024 | 0.8201999893570201 | `pdf_6fec389acaf110ab::chunk::0004` |
| 3 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (11,) | 0.9320361018180847 | 0.8437851330543799 | `soc_2020::chunk::0044` |
| 4 | You may also like | Table III. Charging times up to 100% SOC at different cycle numbers. | (11,) | 0.9116369485855103 | 0.8188651120344801 | `doi_10.1149_1945-7111_a08c3b1a::chunk::0051` |
| 5 | Extreme Fast Charge Challenges for Lithium-ion Battery: Variability and Positive Electrode Issues | Experimental | (5,) | 0.9107916355133057 | 0.8248462982749802 | `tanim_2015::chunk::0008` |
| 6 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 4. Conclusion | (12,) | 0.9082881808280945 | 0.8245401220081242 | `doi_10.1016_j.jpowsour.2019.03::chunk::0061` |
| 7 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | You may also like | (1,) |  |  | `pdf_6fec389acaf110ab::chunk::0003` |
| 8 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) |  |  | `pdf_6fec389acaf110ab::chunk::0005` |
| 9 | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating | (2,) |  |  | `pdf_6fec389acaf110ab::chunk::0006` |
| 10 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Results and Discussion | (11,) |  |  | `soc_2020::chunk::0043` |
| 11 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (12,) |  |  | `soc_2020::chunk::0045` |
| 12 | Fast Charging of Li-Ion Cells: Part IV. Temperature Effects and 'Safe Lines' to Avoid Lithium Plating | Conclusions | (12,) |  |  | `soc_2020::chunk::0046` |
| 13 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | (2, 3) |  |  | `doi_10.1149_2.0401906jes::chunk::0012` |
| 14 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | (3,) |  |  | `doi_10.1149_2.0401906jes::chunk::0014` |
| 15 | Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials | Experimental | (3,) |  |  | `doi_10.1149_2.0401906jes::chunk::0015` |
| 16 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 3.3. Experimental results and analysis. | (12,) |  |  | `doi_10.1016_j.jpowsour.2019.03::chunk::0060` |
| 17 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 4. Conclusion | (13,) |  |  | `doi_10.1016_j.jpowsour.2019.03::chunk::0062` |

#### Evidence excerpts

**1. `doi_10.1149_2.0401906jes::chunk::0013`**

qualitative trends observed during fast charging; a more quantitative approach will be taken in subsequent publications. As shown below, RE measurements provide new insights into the phenomenology of Li plating. Experimental Materials.Electrochemical tests were performed using a Gr anode and a Li1.03(Ni0.5Co0.2Mn0.3)0.97O2 (NCM523)cathode.Theanode contained 91.8 wt% graphite (CGP-A12, Philips 66), 2 wt% of carbon black (C45, Timcal), 0.2 wt% oxalic acid and 6 wt% poly(vinylidene difluoride) (PVdF) binder (KF-9300, Kureha). The cathode contained 90 wt% NCM523 (Toda) and 5 wt% of both C45 and PVdF (Solvay 5130). Slurries were coated on battery grade copper and aluminum foils, respectively. ...

**2. `pdf_6fec389acaf110ab::chunk::0004`**

/ % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating Ilya A. Shkrob, Marco-Tulio F. Rodrigues, and Daniel P. Abraham * ,z Chemical Sciences and Engineering Division, Argonne National Laboratory, Lemont, Illinois 60439, United States of America ECS Fast charging of Li-ion batteries would make ' fueling ' of electric vehicles comparable in time to fueling of gasoline-powered cars, increasing consumer appeal of the new technology. Taking the US Department of Energy goal of safe 6 C charging to 80% capacity as a guide, we describe approaches that can mitigate Li plati...

**3. `soc_2020::chunk::0044`**

, and elsewhere we use it to prescribe pulse sequences that avoid LPC while providing an average charge rate, well in excess of 4C, that precludes Li-plating. Conclusions Constant current and pulse current charging were conducted on NCM523/Gr cells containing a Li-metal reference electrode at 30 °C, 37 °C, 45 °C, and 55 °C. By repeating the experiment for many C-rates we mapped the currents at which the anode potential (as measured by the reference electrode) reached or crossed zero vs Li/Li + . We used these maps, and a state-of-the art multiphase electrochemical model, to compute the currents at which anode surface potential reaches zero vs Li/Li + , thereby determining the boundary of ...

**4. `doi_10.1149_1945-7111_a08c3b1a::chunk::0051`**

ions out of the plated lithium. - Experimental veri fi cation of the protocol in BIL test station. - Reduction of charging time and extension of cycle life. Table III. Charging times up to 100% SOC at different cycle numbers. Compared with 2C CC/CV charging, the charging time is reduced 32% and 25% up to 80% and 100% SOC, respectively and the degradation becomes less after 160 cycles. Future work will include optimization of the fast charging protocol considering the temperature effects and cooling power of battery pack. Appendix A: List of Model Parameters (a: Manufacturers; b: Tuning with the Model; c: Literature)

**5. `tanim_2015::chunk::0008`**

charging. These issues are often overlooked due to the focus on Li metal plating during fast charging, but have the potential to significantly impact the eventual application and use of fast charging. Experimental Table I lists the material, electrode, cell design parameters, and Table II includes the charging protocols. Graphite (1506T Superior Graphite) and NMC532 (Toda America) were used as respective negative and positive electrode active materials, respectively, to fabricate electrodes at the Cell Analysis, Modeling, and Prototyping (CAMP) Facility at Argonne National Laboratory (Argonne). These electrodes were cut and assembled in single layer pouch cells with Celgard 2320 separator...

**6. `doi_10.1016_j.jpowsour.2019.03::chunk::0061`**

% SOC = 6.08 min. OFC-T, 80% SOC = 18.01 min. OFC-T, 100% SOC = 47.91 min 4. Conclusion An online optimal fast charging method was proposed based on a reduced electrochemical model that embeds submodels for side reaction, lithium plating and stripping as a function of temperature. The experimentally validated models are used to analyze the effects of Crates and temperature on the side reaction and lithium plating and then find out the optimal temperatures at different C-rates. At the optimal temperatures, the battery has the longest cycling life. Then, the nonlinear model predictive control is used to determine charging currents and operating temperatures. In order to recover the ions out...

**7. `pdf_6fec389acaf110ab::chunk::0003`**

sealed battery test cell! For precise long-term measurements of solid-state cell chemistries Learn more on our product website: Download the data sheet (PDF): You may also like Half cell SiC480 + LPSCI vs. In/lnLi Coulombic efficiency / % Or contact us directly: - +49 40 79012-734 sales@el-cell.com - www.el-cell.com

**8. `pdf_6fec389acaf110ab::chunk::0005`**

accounts for these observations and provides a means to extrapolate the approach to other cell designs and operation regimes, drawing the maximum average fast charging rates that can still avoid Li plating. Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating © 2021 The Author(s). Published on behalf of The Electrochemical Society by IOP Publishing Limited. This is an open access article distributed under the terms of the Creative Commons Attribution 4.0 License (CC BY, http://creativecommons.org/licenses/ by/4.0/), which permits unrestricted reuse of the work in any medium, provided the original work is properly cited. [DOI: 10.1149/ 1945-7111/...

**9. `pdf_6fec389acaf110ab::chunk::0006`**

which Li plating becomes competitive with Li intercalation, causing severe performance loss. 11 As this damage can be extensive, 10 fast charging regimes that avoid Li plating are required. Fast Charging of Li-Ion Cells: Part V. Design and Demonstration of Protocols to Avoid Li-Plating The Li plating occurs when the overpotential for this electrochemical reaction becomes negative (hereafter all potentials are given vs Li/Li + ). 2,12 -14 This overpotential is between the anode and liquid electrolyte at their interface, and it becomes more positive with increasing anode depth from the separator. For this reason, the overpotential at the separator is the critical indicator for Li plating, a...

**10. `soc_2020::chunk::0043`**

migration in the LiCx electrode accelerates significantly at high rates when the graphite lattice becomes strained. It was impossible to model the fast charge regimes without taking this effect into account. Results and Discussion Figures 14a and 14b present simulations of the ' safe lines ' in Figures 10a and 10b. Using the model, we calculated the ' safe line ' for the anode surface potential η a which is not accessible experimentally. As seen from the plot, due to potential drop across the electrolyte- fi lled separator, the difference between the crossing currents corresponding to these anode potentials systematically increases with the current rate. The overall shape of these ' safe ...

**11. `soc_2020::chunk::0045`**

on the graphite anode) with lower C-rates, thinner electrodes, and higher temperatures (see Fig. 12). For a 70 μ m thick electrode, full cell capacity can Conclusions Figure 14. A numerical simulation of the ' safe lines ' shown in Fig. 10 plotted over an extended range in both axes. The crossing (a) times and (b) lithiation x transferred by a rectangular pulse applied at 3.57 V are plotted vs the charge C-rate ( the vertical axis ). The empty and fi lled symbols are for the anode reference and surface potentials, respectively, for 30 °C ( circles ) and 45 °C ( squares ). The difference between the two potentials increases with the C-rate. For a fi xed time/ lithiation, the C-rates below ...

**12. `soc_2020::chunk::0046`**

, whereas only 56% of the capacity can be reached at a 6C rate. In contrast, only 25% capacity can be achieved at 30 °C at this rate. Conclusions 3. For pulsed charge, the likelihood of Li plating increases considerably with increasing rate and duration of the pulse but decreases with the increasing temperature (see Fig. 14). We give the general methodology of obtaining the ' safe lines ' for different charge regimes without crossing into the Li plating ' danger zone ' during the measurement. This allows mapping of the boundaries in rich detail. 4. At all temperatures, cell relaxation displays stretched exponential (Kohlrausch) kinetics, which includes a fast exponential component and a s...

**13. `doi_10.1149_2.0401906jes::chunk::0012`**

offset can be minimized by using a highly conductive electrolyte and further reduced by placing the RE very close to the electrode (e.g., by using a Luggin capillary). 4 Fast Charging of Li-Ion Cells: Part I. Using Li/Cu Reference Electrodes to Probe Individual Electrode Potentials There is a vast literature on cell configurations for 3-electrode tests in Li-ion batteries, mostly in the context of electrochemical impedance spectroscopy (EIS). 11,16-20 As the a.c. currents are low, the EIS experimental designs are flexible, and artifacts arising from improperly constructed REs are easily identifiable. Validating electrode potentials for Li-ion cells operated in realistic d.c. current regim...

**14. `doi_10.1149_2.0401906jes::chunk::0014`**

at 120°C for 12 h before cell assembly. The cells contained 1.6 mL of liquid electrolyte, which exceeds the combined pore volumes of the electrodes and separators. Experimental Most of the tests used a 1.2 mol/dm 3 lithium hexafluorophosphate (LiPF6) in a 3:7 wt/wt mixture of ethylene and ethyl methyl carbonates ('Gen2,' Tomiyama) as electrolyte. In some experiments, 0.7 M of lithium bis(oxalate)borate (LiBOB) was used as the electrolyte salt instead of 1.2 M LiPF6. In the following narrative, these cells are referred to as LiPF6 and LiBOB cells, respectively.

**15. `doi_10.1149_2.0401906jes::chunk::0015`**

the electrolyte salt instead of 1.2 M LiPF6. In the following narrative, these cells are referred to as LiPF6 and LiBOB cells, respectively. Experimental Cell assembly.Three-electrode cells were assembled using custom-made test stations discussed elsewhere. 13,23 Each cell included 20.3 cm 2 electrode disks spaced by two layers of a 25 μ m thick microporous separator (Celgard 2325). Lithium metal was plated in situ onto the tip of a thin copper wire (25 μ m dia.) to form a microprobe RE; only a 2-3 mm portion of this wire was exposed to the electrolyte and coated with Li, the remaining being insulated by polyurethane coating. The copper wire was lithiated at 5 μ A for 6 h, with the cathod...

**16. `doi_10.1016_j.jpowsour.2019.03::chunk::0060`**

closest to that of 1 C CC/ CV charging. The above analysis s that the design FC protocol (OFC-T) significantly reduces the charging time and degradation speed. 3.3. Experimental results and analysis. Table 5 Charging time at different SOC intervals using different charging protocols. CC/CV (1 C), 40% SOC = 23.23 min. CC/CV (1 C), 80% SOC = 46.67 min. CC/CV (1 C), 100% SOC = 78.13 min. CC/CV (2 C), 40% SOC = 11.63 min. CC/CV (2 C), 80% SOC = 26.37 min. CC/CV (2 C), 100% SOC = 52.60 min. CC/CV (2.7 C), 40% SOC = 9.33 min. CC/CV (2.7 C), 80% SOC = 17.73 min. CC/CV (2.7 C), 100% SOC = 48.60 min. CC/CV (3 C), 40% SOC = 7.73 min. CC/CV (3 C), 80% SOC = 15.83 min. CC/CV (3 C), 100% SOC = 45.60 m...

**17. `doi_10.1016_j.jpowsour.2019.03::chunk::0062`**

reaction rate becomes less but the lithium plating rate increases. Fig. 13. Comparison of different charging protocols. (a) Charging protocols; (b) capacity fade. 4. Conclusion - Active variation of operating temperature along with current profiles optimized by nonlinear model predictive control significantly enables extension of cycle life by suppressing side reaction and lithium plating. - Since pulse discharging current promotes the lithium stripping and recovers ions out of the plated lithium, a higher charging current can be applied than that commonly derived by limiting the overpotential to prevent lithium plating. Therefore, the charging time is further reduced without imposing any...

---

## Query 4: Analogue transfer to an LFP cylindrical cell

### Exact query

> Propose a conservative experimental starting protocol for a graphite/LFP cylindrical cell at 10 °C charging from 10% to 80% SOC when no exact-match protocol is available. Identify which recommendations are transferred from analogous chemistries or form factors, explain the similarities and differences, and state the validation measurements required before increasing current.

### Intended test

Whether the model discloses cross-system extrapolation, uncertainty, assumptions, and validation needs rather than implying direct support.

### Supplied operating conditions

- chemistry: graphite/LFP
- form_factor: cylindrical
- temperature: 10 °C
- soc_range: 10-80%
- objective: conservative starting protocol with explicit analogue transfer

### Execution and validation

- Validation: `pass_with_warnings`
- Warnings: 2
- Agent rounds: 3
- Tool calls: 8
- JSON repair attempts: 0
- Input tokens: 8762
- Output tokens: 2394
- Total tokens: 11156
- Elapsed seconds: 51.26
- Retrieved chunks retained: 16
- Distinct papers retained: 6

#### Validation warnings

- protocol_suggestions[1] contains numerical values not found verbatim in cited evidence: 10 °C
- protocol_suggestions[2] contains numerical values not found verbatim in cited evidence: 10 °C

### Generated answer

For a graphite/LFP cylindrical cell at 10 °C and 10–80% SOC, the literature does not provide an exact-match validated protocol. The most directly relevant cylindrical LFP/graphite evidence supports a multistage charge that uses higher current at low SOC and lower current as SOC rises, because internal resistance is lowest early in charge and rises rapidly above about 70% SOC [ansean_2012::chunk::0012, ansean_2012::chunk::0011, ansean_2012::chunk::0013]. A separate LFP/graphite cylindrical study reports a manufacturer fast-charge recommendation of 3.6C CC-CV for an APR18650M1A cell, but that was at 30 °C and with a different objective than conservative low-temperature starting [attia_1994::chunk::0033, attia_1994::chunk::0034]. Cross-paper synthesis suggests starting below that manufacturer fast-charge rate at 10 °C and using a conservative staged approach, then increasing current only after confirming no plating indicators and acceptable thermal/voltage behavior. Evidence from graphite-based cells at low temperature shows charging current should decrease as temperature falls, and that low-temperature/high-current charging can drive anode potential negative and increase plating risk [doi_10.1016_j.jpowsour.2019.04.047::chunk::0044, tomaszewska_2019::chunk::0078, doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0042].

#### Protocol suggestions

**1. Start with a conservative multistage CC-CV-style profile transferred from cylindrical LFP/graphite evidence: use a higher current only in the low-SOC region, then step down current as SOC approaches the mid/high range, and finish with a short CV hold near the upper cutoff.**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: The cylindrical LFP study reports that internal resistance is lowest immediately after charge start, remains nearly constant from about 10% to 70% SOC, and then rises rapidly; the authors therefore used 4C early, then 1C, then a short CV stage, with a 12% security margin below the manufacturer limit [ansean_2012::chunk::0012, ansean_2012::chunk::0013, ansean_2012::chunk::0011]. For a 10 °C starting point, the same structure is the closest direct analogue, but the current should be treated conservatively because low temperature reduces charge acceptance and increases plating risk in graphite cells [doi_10.1016_j.jpowsour.2019.04.047::chunk::0044, tomaszewska_2019::chunk::0078].
- Applicable conditions: graphite/LFP cylindrical cell; 10 °C ambient or cell temperature; charging from 10% to 80% SOC; no exact-match protocol available
- Limitations: The cited LFP cylindrical protocol was tested at 23 °C, not 10 °C.; The exact current values are not validated for this cell or temperature.; The evidence supports the staged concept, not a deployment-ready recipe.
- Evidence chunks: `ansean_2012::chunk::0012`, `ansean_2012::chunk::0011`, `ansean_2012::chunk::0013`, `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044`, `tomaszewska_2019::chunk::0078`

**2. Use a lower-than-manufacturer fast-charge starting current at 10 °C, rather than transferring the 3.6C cylindrical LFP recommendation directly.**

- Origin: `synthesized`
- Confidence: `low`
- Rationale: A commercial cylindrical LFP/graphite cell had a manufacturer-recommended fast-charge protocol of 3.6C CC-CV, but that was reported for a different test condition set and at 30 °C [attia_1994::chunk::0033, attia_1994::chunk::0034]. Low-temperature graphite-cell evidence shows charging current should be reduced as temperature decreases, and that higher current at low temperature can push anode potential negative and increase plating risk [doi_10.1016_j.jpowsour.2019.04.047::chunk::0044, tomaszewska_2019::chunk::0078]. Therefore, the safest transfer is to start below the 3.6C reference and only increase after validation measurements are clean.
- Applicable conditions: graphite/LFP cylindrical cell; 10 °C; initial experimental screening
- Limitations: No source gives a validated 10 °C current ceiling for this exact cell.; The 3.6C value is manufacturer-reported for a specific cell and condition set, not a universal limit.; The low-temperature evidence is from analogous graphite-based cells and a review, not this exact cell.
- Evidence chunks: `attia_1994::chunk::0033`, `attia_1994::chunk::0034`, `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044`, `tomaszewska_2019::chunk::0078`

**3. Before increasing current, require validation that the cell remains free of plating indicators and stays within acceptable thermal/voltage behavior during the 10% to 80% SOC window.**

- Origin: `synthesized`
- Confidence: `medium`
- Rationale: Low-temperature graphite-cell studies and model-based work emphasize that plating risk rises when anode potential becomes negative and that charging should stop or be limited when plating is approached [doi_10.1016_j.jpowsour.2019.04.047::chunk::0044, doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0042, doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0044]. The LFP cylindrical multistage paper also ties the staged reduction in current to rising internal resistance and temperature control [ansean_2012::chunk::0012, ansean_2012::chunk::0013]. Thus, current should only be increased after confirming no evidence of plating and no problematic temperature rise or voltage-profile distortion.
- Applicable conditions: any candidate starting protocol at 10 °C; graphite anode cells; decision to raise current
- Limitations: The exact validation thresholds are not specified in the cited papers.; The model-based plating criterion is not a direct experimental plating measurement.; This is a conservative screening recommendation, not a validated optimization result.
- Evidence chunks: `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044`, `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0042`, `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0044`, `ansean_2012::chunk::0012`, `ansean_2012::chunk::0013`

#### Conflicting evidence

- The cylindrical LFP study supports a relatively aggressive 4C early-stage current at 23 °C with a 12% margin below the manufacturer limit [ansean_2012::chunk::0013], whereas low-temperature graphite-cell evidence and review material indicate that current should be reduced as temperature falls and that high current at low temperature increases plating risk [doi_10.1016_j.jpowsour.2019.04.047::chunk::0044, tomaszewska_2019::chunk::0078].
- The manufacturer-reported 3.6C CC-CV fast-charge protocol for a cylindrical LFP/graphite cell was reported at 30 °C [attia_1994::chunk::0033, attia_1994::chunk::0034], which conflicts with the need for a more conservative starting point at 10 °C.

#### Missing information

- Exact cell model, capacity, and manufacturer charge limits for the target cylindrical graphite/LFP cell.
- Whether 10 °C refers to ambient temperature, cell temperature, or both.
- Upper cutoff voltage and any manufacturer-specific CC-CV termination current.
- Direct experimental plating diagnostics available for this cell, such as reference-electrode anode potential, post-charge dQ/dV, or microscopy.
- Thermal limits, internal resistance, and allowable temperature rise for the target cell.

#### Safety notes

- Do not transfer the 4C or 3.6C values as-is to 10 °C without validation.
- At low temperature, prioritize plating avoidance over charge-time minimization.
- If anode potential, voltage profile, or temperature behavior suggests plating or abnormal polarization, current should not be increased.
- The literature here does not validate a deployment-ready protocol for this exact cell and condition set.

#### Follow-up questions

- What is the exact cell model and manufacturer-recommended charge limit for the target cylindrical graphite/LFP cell?
- Is 10 °C the ambient chamber temperature or measured cell temperature during charge?
- Can the cell be instrumented with a reference electrode or other plating-sensitive diagnostic during the first trials?
- What voltage cutoff and CV termination current are intended for the 10% to 80% SOC window?
- What thermal rise, impedance growth, or capacity-loss criteria will be used to decide whether to increase current?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | (7,) | 0.8712437152862549 | 0.7902939937726542 | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044` |
| 2 | Fast charging technique for high power lithium iron phosphate batteries: A cycle life analysis | 2.2. Fast-charging protocol | (2, 3) | 0.8646580576896667 | 0.7961730201933166 | `ansean_2012::chunk::0012` |
| 3 | Lithium-ion battery fast charging: A review | 5.1. Types of charging protocols | (13, 14) | 0.8625415563583374 | 0.81541947756883 | `tomaszewska_2019::chunk::0078` |
| 4 | Closed-loop optimization of fast-charging protocols for batteries with machine learning | Experimental | (7,) | 0.8558632731437683 | 0.7853117134016315 | `attia_1994::chunk::0034` |
| 5 | You may also like | Screening of Conventional Protocols Using the Pseudo2D Model | (5,) | 0.8520684838294983 | 0.8018939077515487 | `unknown_2020::chunk::0022` |
| 6 | Closed-loop optimization of fast-charging protocols for batteries with machine learning | Experimental | (7,) | 0.8747797608375549 | 0.7653707601797152 | `attia_1994::chunk::0033` |
| 7 | Uncertainty-aware state estimation for electrochemical model-based fast charging control of lithium-ion batteries | 5. Charging control | (9,) | 0.8581069111824036 | 0.7698045110320108 | `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0043` |
| 8 | Fast charging technique for high power lithium iron phosphate batteries: A cycle life analysis | 2.2. Fast-charging protocol | (2,) |  |  | `ansean_2012::chunk::0011` |
| 9 | Fast charging technique for high power lithium iron phosphate batteries: A cycle life analysis | 2.2. Fast-charging protocol | (3,) |  |  | `ansean_2012::chunk::0013` |
| 10 | Closed-loop optimization of fast-charging protocols for batteries with machine learning | Online content | (6,) |  |  | `attia_1994::chunk::0032` |
| 11 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | (7,) |  |  | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0043` |
| 12 | Fast charging of an electric vehicle lithium-ion battery at the limit of the lithium deposition process | 4.1. Three-electrode test cell level | (7,) |  |  | `doi_10.1016_j.jpowsour.2019.04.047::chunk::0045` |
| 13 | Lithium-ion battery fast charging: A review | 5.1. Types of charging protocols | (13,) |  |  | `tomaszewska_2019::chunk::0077` |
| 14 | Lithium-ion battery fast charging: A review | 5.1. Types of charging protocols | (13, 14) |  |  | `tomaszewska_2019::chunk::0079` |
| 15 | Uncertainty-aware state estimation for electrochemical model-based fast charging control of lithium-ion batteries | 5. Charging control | (9,) |  |  | `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0042` |
| 16 | Uncertainty-aware state estimation for electrochemical model-based fast charging control of lithium-ion batteries | 5. Charging control | (9,) |  |  | `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0044` |

#### Evidence excerpts

**1. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0044`**

Time to 80% SOC = ± 123.6 min 0.6%. -5°C, Time to 100% SOC = ± 207.0 min 0.9% 4.1. Three-electrode test cell level Taking a look at the current map, the anticipated dependency that the charging current is monotonically increasing with temperature is striking. Inversely, the charging time to 100% SOC increases by tenfold from 45°C to -5°C. The maximum charging current at low SOC goes down from 9C at temperatures of 30°C to 1.1C at -5°C. Interpreting the shape of the current curves in dependency of the SOC in the CVneg phase, the current curves ' slope decreases rapidly at low SOC until it stays almost constant for greater SOCs. At the end of the charging process the current at 45°C goes do...

**2. `ansean_2012::chunk::0012`**

: it starts at an ambient temperature of 23 ° C, increases by 2 ° C to its maximum at approximately half the charging time, and ends back at the ambient temperature. 2.2. Fast-charging protocol The multistage fast charging technique is based on the evolution of internal resistance during the charging sequence. Fig. 3 shows the results of the internal resistance evolution versus the SOC for charging calculated with Eq. (1) using C/25 and 4 C currents. The internal resistance reaches its minimum immediately after starting the charging process. As the cell reaches approximately 10% SOC, the internal resistance remains practically constant at 15 e 16 m U until 70% SOC is achieved, after which...

**3. `tomaszewska_2019::chunk::0078`**

shown to achieve reduced charging times, increased ef fi ciencies and/or improved capacity or power retention. Fig. 8 illustrates some of the alternative protocols proposed for fast charging. 5.1. Types of charging protocols Zhang et al. [192] studied the effects of the CC-CV charging protocol on the reversible capacity and anode potential evolution in experimental LCO/graphite cells with embedded reference electrodes as they were charged at ambient temperatures from -20 + C to 10 + C with C-rates between 0.16C and 1.2C. The results showed a positive correlation between increasing charging current in the CC phase and increasing time taken by the CV phase to complete. The authors observed ...

**4. `attia_1994::chunk::0034`**

. The graphite and LFP electrodes are 40 μm thick and 80 μm thick, respectively, as quantified via X-ray tomography (Zeiss Xradia 520 Versa). Experimental The cells were cycled with various charging protocols but identically discharged. Cells were charged with one of 224 candidate six-step, tenminute charging protocols from 0% to 80% SOC, as detailed below. After a five-second rest, all cells then charged from 80% to 100% SOC with a 1C CC-CV charging step to 3.6 V and a current cutoff of C/20. After another five-second rest, all cells subsequently discharged with a CC-CV discharge at 4C to 2.0 V and a current cutoff of C/20. The cells rested for another five seconds before the subsequent ...

**5. `unknown_2020::chunk::0022`**

-of-charge after 10 min charging using CCCV or CPCV protocol. The colorbar of the symbols re fl ect the mean cell temperature during the charging process. Screening of Conventional Protocols Using the Pseudo2D Model To investigate how the charge rate in fl uences the driving force of lithium plating, a parameter sweep is performed such that the investigated cell is charged with a wide range of n C CCCV and n P CPCV protocols, up to 10C and 10P, respectively. Figure 3 summarizes the simulation results, the x axis of which is the state-ofcharge (SOC = ò I t d /(35.25 mAh)) of the cell after 10 min charging while the y axis is the maximum driving force for lithium plating during the charging...

**6. `attia_1994::chunk::0033`**

Publisher's note Springer Nature remains neutral with regard to jurisdictional claims in published maps and institutional affiliations. - © The Author(s), under exclusive licence to Springer Nature Limited 2020 Experimental Commercial high-power lithium iron phosphate (LFP)/graphite A123 APR18650M1A cylindrical cells were used in this work (packing date 2015-09-26, lot number EL1508007-R). These cells have a nominal capacity of 1.1 A h and a nominal voltage of 3.3 V. All currents are defined in units of C rate; here, 1C is 1.1 A, or the current required to fully (dis) charge the nominal capacity (1.1 A h) in 1 h. The manufacturer's recommended fast-charging protocol is 3.6C (3.96 A) CC-CV...

**7. `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0043`**

at an SOC of 10% and stopped at an SOC of 80% or the beginning of lithium plating. The setpoint of the anode voltage controller is fixed to 1 mV. 5. Charging control The simulation results are depicted in Fig. 5. The left column shows current, anode potential and temperature for controlled charging while the right column depicts the results for CC-charging. The current of the CC-charging scheme was set to the average current of the controlled charging simulations, which is approximately 2.1 C at 0 � C and 1.7 C at -5 � C, resulting in similar charging overall times. This charging speed is also above the specified 2 C which are allowed above 0 � C. An SOC of 80% was reached after 22 and 29...

**8. `ansean_2012::chunk::0011`**

C. The temperatures in both the climate chamber and the cell case were measured with T-type copper-constantan thermocouples and logged into the Arbin system. 2.2. Fast-charging protocol The proposed multistage fast charging technique pro fi le is shown in Fig. 2. The charging process is split into three different stages, referred as CC-I, CC-II and CV-I. The fi rst stage (CC-I) starts with a constant current at 4 C to the charging cut-off voltage (3.6 V). The second stage (CC-II) is a constant current charge at 1 C. Since the current in CC-II is lower than in CC-I, the cell voltage drops below 3.6 V (see Fig. 2 (b)) allowing the charge to be extended, until the cell reaches again the char...

**9. `ansean_2012::chunk::0013`**

prototype power cells from the same manufacturer [19]. Fig. 2. Current, voltage, state of charge and temperature pro fi les for the fast-charging technique. 2.2. Fast-charging protocol Because of the internal resistance behavior, the highest charging current 4 C is applied when the cell ' s internal resistance is at the lower values. This approach results in a more energy ef fi cient charging process. The last two stages of the charging process are applied as the cell ' s internal resistance increases rapidly; this procedure helps to decrease the cell ' s temperature to its initial value (see Fig. 2 (d)). The charging current rate at 4 C was selected because it is close to the maximum cha...

**10. `attia_1994::chunk::0032`**

Hastie, T. Regularization and variable selection via the elastic net. J. R. Stat. Soc. Ser. B 67 , 301-320 (2005). Online content 28. Keil, P. et al. Calendar aging of lithium-ion batteries. I. Impact of the graphite anode on capacity fade. J. Electrochem. Soc . 163 , A1872-A1880 (2016). 29. Wood, D. L., Li, J. & Daniel, C. Prospects for reducing the processing cost of lithium ion batteries. J. Power Sources 275 , 234-242 (2015). 30. Zimmerman, A. H., Quinzio, M. V. & Monica, S. Adaptive charging method for lithium-ion battery cells. US Patent US6204634B1 (2001). 31. Park, S., Kato, D., Gima, Z., Klein, R. & Moura, S. Optimal experimental design for parameterization of an electrochemical ...

**11. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0043`**

, Time to 100% SOC = ± 59.6 min 2.7%. 10°C, Time to 80% SOC = ± 48.2 min 1.3%. 4.1. Three-electrode test cell level 10°C, Time to 100% SOC = ± 78.8 min 1.9%. 5°C, Time to 80% SOC = ± 63.2 min 1.4%. 5°C, Time to 100% SOC = ± 104.0 min 1.6%. 0°C, Time to 80% SOC = ± 87.1 min 1.3%. 0°C, Time to 100% SOC = ± 145.7 min 1.4%. -5°C, Time to 80% SOC = ± 123.6 min 0.6%. -5°C, Time to 100% SOC = ± 207.0 min 0.9%

**12. `doi_10.1016_j.jpowsour.2019.04.047::chunk::0045`**

1C. The shape of the curves mainly depends on the present surface concentration of lithium of the graphite particles and the slow di ff usion of lithium inside the solid particles. 4.1. Three-electrode test cell level Table 2 indicates the charging times at the di ff erent ambient temperatures. A charging time for a charge from 0% to 80% SOC in less than 15min without lithium deposition is possible for ambient temperatures greater than or equal to 40°C at three-electrode test cell level. Regarding the battery's system limit of 5C, at pouch cell level 80% SOC is reached in 13.9min (test setup A, ∇ = f 0% ), 15.2min (test setup B, ∇ = f 10% ) or 15.6min (test setup C, ∇ = f 10% , = ΔSOC 2% ...

**13. `tomaszewska_2019::chunk::0077`**

in a signi fi cantly shorter time. Charging strategies, which determine how the current density is varied during the charging process, are an important category of such solutions. 5.1. Types of charging protocols Standard protocols. Numerous charging protocols have been proposed for Li-ion batteries. CC-CV is by far the most common one. It consists of a constant current charging phase where the battery voltage increases up to a cut-off value (CC phase), followed by a constant voltage hold until the current falls to near-zero (CV phase). The CV phase allows for the concentration gradients within the electrode particles to disperse and is usually necessary to obtain high capacity utilisatio...

**14. `tomaszewska_2019::chunk::0079`**

number of cycles at 0.5C CC-CV at -10 + C, resulting in an elevated average voltage in the CC stage and longer duration of the CV stage. 5.1. Types of charging protocols In comparison, the voltage pro fi le of cells charged at 0.2 and 0.3C at the same temperature retained a similar shape. The increased average voltage as a result of repeated cycling at higher C-rates may contribute to increased degradation rate. Fig. 8. Schematic representation of common types of charging protocols proposed for fast charging. a) Constant Current - Constant Voltage (CC-CV), b) Constant Power - Constant Voltage (CP-CV), c) Multistage Constant Current - Constant Voltage (MCC-CV), d) Pulse charging, e) Boostc...

**15. `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0042`**

charge. Both simulations were stopped at the beginning of the CV-phase. decreased and the resulting error can be mitigated by keeping a safety margin during current control. 5. Charging control To quantify the benefits of plating side reaction potential controlled charging, we conducted several simulations where conventional con­ stant current charging is taken as a benchmark. To reduce the influence of discretization errors, the model is discretized with three particles per electrode and 60 shells per particle for this analysis.As plating is likely to occur at low temperatures, we analyze the cell performance at ambient temperatures of 0 � C and -5 � C. According to the data sheet, charg...

**16. `doi_10.4121_uuid_30a44cee-f94e-466d-a2e0-6239d5fa6bbb::chunk::0044`**

that overpotentials are effec­ tively lowered. Temperature decreases later on, when the current 5. Charging control is lowered due to anode side reaction potential limitations. The tempera­ ture increase is in line with [26] who measured a temperature increase to 23 � C when charging with 4 C at 0 � C ambient temperature for the same cell. In contrast to this, the CC-Profile shows a lower peak temperature but no cool down in the course of the charge. According to the intended side reaction potential limitation, charging currents are too high from approximately 40 to 50% SOC onwards, so that lithium plating is ex­ pected to occur.

---

## Query 5: Insufficient-evidence and unsafe-generalization challenge

### Exact query

> Give one validated universal protocol that charges any lithium-ion battery from 0% to 100% SOC in 10 minutes at temperatures from -10 °C to 45 °C.

### Intended test

Whether the system refuses unsupported universality, identifies missing cell-specific limits, and avoids fabricating safety-critical parameters.

### Supplied operating conditions

- chemistry: any lithium-ion chemistry
- form_factor: any
- temperature: -10 °C to 45 °C
- soc_range: 0-100%
- objective: universal 10-minute charge

### Execution and validation

- Validation: `pass`
- Warnings: 0
- Agent rounds: 3
- Tool calls: 6
- JSON repair attempts: 0
- Input tokens: 6441
- Output tokens: 1506
- Total tokens: 7947
- Elapsed seconds: 51.61
- Retrieved chunks retained: 10
- Distinct papers retained: 4

### Generated answer

No validated universal protocol was found that can charge any lithium-ion battery from 0% to 100% SOC in 10 minutes across -10 °C to 45 °C. The retrieved evidence is chemistry-, cell-design-, and model-specific, and the fastest reported/optimized protocols generally target partial SOC windows or specific cells, often with lithium-plating constraints and temperature control. Some papers report 10-minute charging to ~73–80% SOC under specific NMC/graphite or modeled cells, and one experimental fast-charge protocol reached 0% to 85% SOC in 26.8 min at 25 °C, but none support the requested universal full-charge claim.

#### Protocol suggestions

**1. Use a model-informed, plating-constrained multi-stage charge with current reductions triggered by lithium-deposition onset, then tune the schedule per cell chemistry and temperature.**

- Origin: `reported`
- Confidence: `medium`
- Rationale: A stepwise protocol reduced current before lithium deposition onset and was experimentally validated on three cells; the paper reports 0% to 85% SOC in 26.8 min with >95% SoH after 100 cycles at 25 °C.
- Applicable conditions: Graphite-based Li-ion cells in the cited study; Temperature held constant at 25 °C in validation; 0% to 85% SOC demonstrated in 26.8 min for one constrained pouch-cell study
- Limitations: Not universal across chemistries or form factors; Does not achieve 0% to 100% SOC in 10 min; Validation was at 25 °C, not -10 °C to 45 °C
- Evidence chunks: `doi_10.1149_1945-7111::chunk::0049`

**2. Use an electrochemical-thermal, plating-constrained optimization framework to generate cell-specific 10-minute protocols, optionally with temperature control and pulse discharge for stripping plated lithium.**

- Origin: `reported`
- Confidence: `medium`
- Rationale: The paper reports a validated model used to optimize charging currents and operating temperatures, and to add pulse discharging currents for lithium stripping; it also reports that 10-minute charging to about 73% SOC is possible with 10C CCCV but with high plating driving force and elevated mean temperature.
- Applicable conditions: NMC532/graphite modeled cell in the cited work; 10-minute charging objective; Temperature-aware operation with active thermal control
- Limitations: Model- and cell-specific, not universal; Reported results are far below 100% SOC in 10 min; Temperature requirements and operating limits are not given for the full -10 °C to 45 °C range
- Evidence chunks: `unknown_2020::chunk::0013`, `unknown_2020::chunk::0022`, `doi_10.1016_j.jpowsour.2019.03::chunk::0061`

**3. Use a practical multi-stage CC/CCCV or CC-to-voltage-ramping protocol as a compromise for faster 10-minute charging, but only after cell-specific parameterization.**

- Origin: `synthesized`
- Confidence: `low`
- Rationale: Across the retrieved studies, multi-stage CC, CCCV/CPCV, and voltage-ramping variants are presented as practical approximations to semi-optimal protocols; they can improve no-plating capacity relative to standard CCCV in the studied cell, but remain cell-specific and do not establish universal full-charge capability.
- Applicable conditions: NMC532/graphite modeled cell; 10-minute charging target; Need for simpler implementation than full online optimization
- Limitations: No evidence of 0% to 100% SOC in 10 min; No evidence of universality across any lithium-ion chemistry; Performance depends on ambient temperature and cell design
- Evidence chunks: `unknown_2020::chunk::0043`, `unknown_2020::chunk::0060`, `unknown_2020::chunk::0061`, `unknown_2020::chunk::0026`

#### Conflicting evidence

- The request asks for a universal 0% to 100% SOC in 10 minutes across -10 °C to 45 °C, but the retrieved evidence only shows partial-charge achievements such as 0% to 85% SOC in 26.8 min at 25 °C and about 73% SOC in 10 min for a modeled NMC532/graphite cell.
- Some studies explicitly note that results are simulation-only or model-based, and experimental validation is ongoing or limited to specific cells, which conflicts with the idea of a validated universal deployment-ready protocol.
- Temperature-aware optimization improves charging and cycle life in specific cells, but the evidence also states that low temperature increases lithium-plating risk and high temperature accelerates side reactions, making a single universal schedule across -10 °C to 45 °C unsupported.

#### Missing information

- No evidence of a protocol validated for any lithium-ion chemistry, any form factor, and the full -10 °C to 45 °C range.
- No evidence of 0% to 100% SOC completion in 10 minutes for any retrieved cell.
- No operating limits were provided for current, voltage, temperature ramp rate, thermal management, or safety constraints.
- No evidence that a single protocol is robust to chemistry differences such as LFP, NMC, or other graphite-based cells.

#### Safety notes

- Fast charging at low temperature can increase lithium-plating risk; high temperature can accelerate side reactions and degradation.
- The retrieved literature uses plating constraints and temperature control to avoid unsafe or damaging conditions, but does not validate a universal protocol for deployment.
- Do not assume that a protocol optimized for one cell or chemistry is safe for another without revalidation.

#### Follow-up questions

- Which specific lithium-ion chemistries and form factors should be prioritized for a narrower, evidence-backed protocol search?
- Is the goal to maximize charge in 10 minutes, or to achieve full charge with acceptable degradation over many cycles?
- Should the search focus on experimentally validated protocols only, or are model-derived protocols acceptable as candidates?

### Retrieved evidence

| # | Paper / record | Section | Pages | Reranker | Vector | Chunk |
|---:|---|---|---|---:|---:|---|
| 1 | You may also like | Results and Discussion | (11,) | 0.887912392616272 | 0.7802724300682777 | `doi_10.1149_1945-7111::chunk::0049` |
| 2 | You may also like | List of symbols | (3,) | 0.8834072947502136 | 0.7910663444400563 | `unknown_2020::chunk::0013` |
| 3 | Closed-loop optimization of fast-charging protocols for batteries with machine learning | Closed-loop optimization of fast-charging protocols for batteries with machine learning | (3,) | 0.8720938563346863 | 0.7642271969150243 | `attia_1994::chunk::0014` |
| 4 | Actively temperature controlled health-aware fast charging method for lithium-ion battery using nonlinear model predictive control | 4. Conclusion | (12,) | 0.8615059852600098 | 0.7896289670601846 | `doi_10.1016_j.jpowsour.2019.03::chunk::0061` |
| 5 | You may also like | Acknowledgments | (13,) | 0.8600096702575684 | 0.7696428738087526 | `unknown_2020::chunk::0068` |
| 6 | You may also like | Screening of Conventional Protocols Using the Pseudo2D Model | (5,) | 0.8577912449836731 | 0.7834771926347006 | `unknown_2020::chunk::0022` |
| 7 | You may also like | Discussion | (12,) | 0.8326045870780945 | 0.7819841189676389 | `unknown_2020::chunk::0060` |
| 8 | You may also like | Discussion | (12,) | 0.8319686055183411 | 0.7589645249510916 | `unknown_2020::chunk::0061` |
| 9 | You may also like | Novel Charging Protocols Without Lithium Plating | (9,) | 0.8316696882247925 | 0.7678546046553355 | `unknown_2020::chunk::0043` |
| 10 | You may also like | Screening of Conventional Protocols Using the Pseudo2D Model | (5, 6) | 0.8302422761917114 | 0.7595866550028714 | `unknown_2020::chunk::0026` |

#### Evidence excerpts

**1. `doi_10.1149_1945-7111::chunk::0049`**

the stepwise protocol is reduced to the next lower current before lithium deposition onset is reached. The resulting fast charging protocol based on onset of lithium deposition is shown in Table II. Results and Discussion The shown fast charge protocol allows a charging of the cell from 0%SoC to 85%SoC in 26.8 min. To validate the developed charging protocol three cells were cycled with this protocol. Start condition was 25 °C ±1 °C cell temperature and the temperature of the chamber held constant. Cells were cycled in the already presented test setup (refer to Fig. 1) to realize the same test conditions as in second test case. The cycling was started at 0%SoC and the cell was charged wit...

**2. `unknown_2020::chunk::0013`**

% in 10 min, with the MCC protocol showing the least variability in cell degradation. Detailed reviews on these fast charging protocols are available in literature. 27,29 -31 List of symbols The objective of this work is to develop model-informed extreme fast charging protocols that make full use of the fast charging potential of a cell with given materials and electrode/cell design. We are especially interested in how much charge can be transferred to a cell within 10 min, with preventing lithium plating being the constraint. Using a LIB electrochemical/thermal model for graphite/NMC532 cells, which was validated versus high rate charge data for cells with several loadings, 8 a semi-opti...

**3. `attia_1994::chunk::0014`**

in 17 min (rate testing data are presented in Extended Data Fig. 2). The cycle life decreases dramatically with faster charging time 4,5 , motivating this optimization. Closed-loop optimization of fast-charging protocols for batteries with machine learning Since the LFP positive electrode is generally considered to be stable 4,5 , we select this battery chemistry to isolate the effects of extreme fast charging on graphite, which is universally employed in lithium-ion batteries.

**4. `doi_10.1016_j.jpowsour.2019.03::chunk::0061`**

% SOC = 6.08 min. OFC-T, 80% SOC = 18.01 min. OFC-T, 100% SOC = 47.91 min 4. Conclusion An online optimal fast charging method was proposed based on a reduced electrochemical model that embeds submodels for side reaction, lithium plating and stripping as a function of temperature. The experimentally validated models are used to analyze the effects of Crates and temperature on the side reaction and lithium plating and then find out the optimal temperatures at different C-rates. At the optimal temperatures, the battery has the longest cycling life. Then, the nonlinear model predictive control is used to determine charging currents and operating temperatures. In order to recover the ions out...

**5. `unknown_2020::chunk::0068`**

reported in this article are based on simulation only. Experimental validation of the proposed fast charging protocols is ongoing to verify their improved extreme fast charging capability and cycle life over traditional protocols. Acknowledgments This work was authored by the National Renewable Energy Laboratory, operated by Alliance for Sustainable Energy, LLC, for the U.S. Department of Energy (DOE) under Contract No. DEAC36-08GO28308. Funding was provided by the U.S. DOE Of fi ce of Vehicle Technology Extreme Fast Charge Cell Evaluation of Lithium-Ion Batteries (XCEL) Program, program manager Samuel Gillard. The views expressed in the article do not necessarily represent the views of t...

**6. `unknown_2020::chunk::0022`**

-of-charge after 10 min charging using CCCV or CPCV protocol. The colorbar of the symbols re fl ect the mean cell temperature during the charging process. Screening of Conventional Protocols Using the Pseudo2D Model To investigate how the charge rate in fl uences the driving force of lithium plating, a parameter sweep is performed such that the investigated cell is charged with a wide range of n C CCCV and n P CPCV protocols, up to 10C and 10P, respectively. Figure 3 summarizes the simulation results, the x axis of which is the state-ofcharge (SOC = ò I t d /(35.25 mAh)) of the cell after 10 min charging while the y axis is the maximum driving force for lithium plating during the charging...

**7. `unknown_2020::chunk::0060`**

min charging using the CCCV protocol and the proposed voltage ramping protocol at (a) T 0 = 30 °C and (b) T 0 = 55 °C. Discussion Also shown in Fig. 13a is the parameter sweeping results for the voltage ramping protocol at T 0 = 36 °C, with the sweeping ranges the same as those introduced in the Constant-current charging followed by voltage ramping section. The superiority of the voltage ramping protocol can be illustrated from two aspects. First, at the same ambient temperature ( T 0 = 36 °C), the voltage ramping protocol can increase the no-plating capacity by 9.5% compared to the CCCV protocol. Second, to achieve 80% charge in 10 min, the temperature requirement for the voltage ramping...

**8. `unknown_2020::chunk::0061`**

shorter warm up time and lower energy consumption for battery heating. It may also contribute to a longer service life as LIBs tend to degrade faster at higher temperature. 50,51 Discussion Figure 13b shows the parameter sweeping results for the multiple CCCV protocol at T 0 = 36 °C, with the sweeping ranges the same as those introduced in the Multiple constant-current constant-voltage charging section. The results of the standard CCCV protocol at different ambient temperatures are also shown in this Fig. for comparision. It can be seen that all the investigated cases outperform the standard CCCV protocol at the same ambient temperature, in terms of the driving force for lithium plating a...

**9. `unknown_2020::chunk::0043`**

versus cell state-of-charge after 10 min charging using the semioptimal protocol. The colorbar of the symbols re fl ect the mean cell temperature during the charging process. Novel Charging Protocols Without Lithium Plating Based on the above observation, the fi rst novel charging protocol is proposed, such that the constant-current charging stage is following by a voltage ramping stage. This protocol only requires three parameters: initial C rate, V switch at which constant-current charging is switched to voltage ramping, and the voltage ramping rate v ramp . In a real charging scenario, the switch voltage V switch needs to be prede fi ned to control when the voltage ramping stage starts...

**10. `unknown_2020::chunk::0026`**

the cell is charged to the same capacity in 10 min, the multi-stage constant-current charging protocol actually yields higher maximum lithium plating driving force for most of the cases. Screening of Conventional Protocols Using the Pseudo2D Model Figure 4. (a) Voltage and C rate pro fi les of the three-stage constant-current charging protocol which charges the cell at 10C, 6C and 4C sequentially. (b) Evolution of f f -s e of the 10C-6C-4C and 5C-4C-3C charging protocols, respectively. Figure 5. (a) Variation of min( f f -s e ) versus cell state-of-charge after 10 min charging using the two-stage and three-stage constant-current charging protocols. The colorbar of the symbols re fl ect th...

---
