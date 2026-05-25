# Electronic Component Selection Framework

## Requirement Intake

Ask only for missing information that materially affects the candidate pool. Use reasonable assumptions for minor details and label them.

Core fields:

- Application and circuit role
- Electrical operating range and absolute limits
- Accuracy, noise, speed, power, timing, or other performance targets
- Interface, firmware/software, and system constraints
- Package, footprint, height, assembly, and temperature range
- Compliance needs: RoHS, REACH, AEC-Q, UL, IEC, ISO, medical, safety, or export controls
- Region, preferred distributors, approved manufacturer list, production-status needs, and second-source policy

## Pass/Fail Gates

Reject candidates before scoring if they fail any gate:

- Operating ratings do not cover the use case with margin.
- Thermal dissipation cannot be handled by the package, board, or cooling approach.
- Accuracy, bandwidth, noise, timing, interface, or protection limits break the design.
- Package, pinout, land pattern, or assembly process is incompatible.
- Production status, lifecycle, source restriction, or compliance status is incompatible with the build.

## Candidate CSV Structure

Use fixed columns for every deliverable and insert dynamic parameter columns between `fit_summary` and `lifecycle`.

Fixed columns:

```csv
rank,part_number,manufacturer,component_type,package,production_status,fit_summary,lifecycle,datasheet_url,risks,validation_needed,score
```

Column behavior:

- `rank`: integer rank after filtering and scoring.
- `part_number`: exact orderable or base part number. Use orderable MPN when package, temperature grade, or reel/tape suffix matters.
- `manufacturer`: component maker, not distributor.
- `component_type`: normalized type such as LDO, buck regulator, ADC, N-MOSFET, TVS diode, connector.
- `package`: package and pin count when available.
- `production_status`: normalized maker/distributor status. Use `production`, `active`, `new`, `preview`, `mature`, `nrnd`, `obsolete`, `eol`, `unknown`, or the exact official status in snake_case when it does not map cleanly.
- `fit_summary`: one short sentence explaining why the part fits or misses.
- `lifecycle`: optional lifecycle detail when distinct from `production_status`; otherwise repeat the same normalized value or write `unknown`.
- `datasheet_url`: official datasheet PDF URL when available; otherwise `not_found`.
- `risks`: supply, thermal, package, lifecycle, compliance, or design risks.
- `validation_needed`: checks still required before design release.
- `score`: 0-100 overall score after pass/fail gates.

Dynamic parameter columns:

- Select parameter columns after understanding the user request and reading candidate datasheets.
- Include one column per meaningful parameter; do not combine specs into semicolon-separated bundles.
- Include columns for every hard user requirement.
- Prefer datasheet names that engineers expect, normalized to snake_case, such as `input_range`, `dropout_voltage`, `rds_on`, `offset_voltage`, or `capacitance`.
- Do not add irrelevant columns just because they appeared in another component type's previous CSV.
- Do not use `param_` prefixes.
- Use `unknown` for missing values; do not fabricate.

Examples:

- ADC: `channels,resolution_bits,input_range,reference,sample_rate,interface,inl,dnl,offset_error,gain_error,snr,temperature_range`
- LDO: `vin_range,vout,output_current,dropout_voltage,iq,noise,psrr,output_accuracy,package_options`
- MOSFET: `vds,id_continuous,rds_on,vgs_drive,vgs_threshold,qg,power_dissipation,package`
- Op amp: `supply_range,gbw,slew_rate,offset_voltage,input_bias_current,noise_density,output_swing,quiescent_current`
- Capacitor: `capacitance,voltage_rating,tolerance,dielectric,case_size,temperature_range,dc_bias_derating,esr`

## Source Requirements

Use source hierarchy in this order:

1. `https://www.analog.com/` and `https://www.ti.com.cn/` official manufacturer pages for electrical parameters, lifecycle, package variants, models, design resources, and datasheet PDFs when the candidate is from ADI or TI.
2. `https://www.mouser.cn` for distributor discovery, packaging, orderable MPNs, lifecycle/production clues, and datasheet links.
3. Other official manufacturer pages only when Analog Devices and TI do not sufficiently cover the requested component type, or when the user explicitly wants more vendors.
4. Other authorized distributors only when Mouser has no useful listing, the part is region-restricted, or the user needs cross-distributor comparison.
5. Third-party parametric databases only as discovery aids; verify critical values from manufacturer or authorized distributor sources before writing them to CSV.

For every row, include exactly one network-address column: `datasheet_url`. Prefer datasheet links from Analog Devices or TI product pages for their own parts; Mouser datasheet links are acceptable when they point to an official PDF. Do not include product-page or search-result URL columns in the CSV.

## Scoring

Use pass/fail gates first. Weighted scores are only meaningful after gates are satisfied.

Suggested scoring categories:

| Category | Weight | What To Consider |
|---|---:|---|
| requirement | 0.35 | Hard requirement match, operating range, mandatory interface/package/standard constraints |
| performance | 0.25 | Accuracy, efficiency, speed, noise, margin, or other key performance metrics for the component type |
| fit | 0.15 | Package, footprint, pinout, layout difficulty, firmware/software impact |
| lifecycle | 0.15 | Production status, active/NRND/obsolete state, maker support, second-source risk |
| validation | 0.10 | Datasheet clarity, eval boards, models, app notes, existing design history |

Optional helper columns for `scripts/score_components.py`:

```csv
score_requirement,score_performance,score_fit,score_lifecycle,score_validation
```

If helper columns are absent or invalid, the script warns and uses a neutral score. If `score_lifecycle` is absent, the script derives lifecycle score from `lifecycle` or `production_status`.

## Search Pattern

Start with the user's component type and constraints:

1. Search Mouser China for broad candidate discovery and orderable part-number data.
2. For ADI candidates, open the matching Analog Devices product page and datasheet.
3. For TI candidates, open the matching TI China product page and datasheet.
4. Write CSV rows only after the part number, package, dynamic parameter values, production status, and datasheet URL are verified or explicitly marked unknown.
5. If Mouser, ADI, and TI do not produce enough credible candidates, state the gap before expanding to other manufacturers or distributors.

## Category Checklists

Power regulators:

- Input voltage, output voltage, current, transient load, efficiency, switching frequency, quiescent current
- Thermal resistance, layout sensitivity, compensation, inductor/capacitor requirements
- EMI behavior, spread spectrum, soft-start, enable, power-good, protection modes

Op amps and comparators:

- Supply range, input common-mode range, output swing, offset, bias current, bandwidth, slew rate
- Noise, stability with load capacitance, rail-to-rail behavior, input protection, package leakage

ADCs and DACs:

- Resolution, ENOB, sample rate, input bandwidth, reference, interface, latency, clocking
- INL, DNL, offset error, gain error, total unadjusted error if specified
- Analog front-end drive, anti-alias filter, grounding, layout, calibration, digital isolation

MCUs and SoCs:

- CPU, memory, peripherals, package, toolchain, boot mode, security, power modes
- Firmware ecosystem, errata, long-term availability, programming and debug access

Passives:

- Value, tolerance, voltage/current rating, temperature coefficient, ESR/ESL, self-resonance
- Derating, package stress, DC bias for MLCCs, power rating, pulse handling

Connectors:

- Pin count, pitch, current, voltage, mating cycles, retention, keying, cable strain relief
- Availability of mating part, assembly method, panel or enclosure fit

RF and clocks:

- Frequency, phase noise, jitter, impedance, output format, tuning range, stability
- Layout reference design, shielding, regulatory band, matching network, simulation model

## Substitution Rules

For alternates, check all of the following:

- Same or better operating ratings under real conditions.
- Pinout and land pattern compatibility, not just package name.
- Control pins, default states, startup timing, and fault behavior.
- Firmware-visible IDs, register maps, timing, and calibration differences.
- Parametric drift across temperature and process.
- Qualification impact and procurement acceptance.

## Deliverables

Quick recommendation:

- 10 candidates by default when the market has enough credible options.
- Fewer than 10 only when the preferred sources do not contain enough credible candidates; explain the shortfall.
- One CSV file with fixed columns plus dynamically selected parameter columns.
- Short chat summary naming the top 2 to 3 candidates.
- Risks and validation tasks.

Detailed selection:

- Requirement gates
- CSV candidate matrix
- Datasheet link and access date
- Datasheet revision/date when available
- Lifecycle and sourcing notes
- Test or simulation plan
