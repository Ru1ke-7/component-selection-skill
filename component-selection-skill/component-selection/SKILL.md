---
name: component-selection
description: Electronic component selection and sourced CSV generation for hardware design. Use when selecting, substituting, or comparing electronic components and producing a CSV of candidate part numbers, dynamic parameter columns, lifecycle/production status, datasheet links, risks, and validation notes.
triggers:
  - "元器件选型"
  - "器件选型"
  - "component selection"
  - "选型.*(LDO|ADC|MOSFET|运放|电源)"
  - "帮我找.*(芯片|元件|器件)"
  - "BOM.*(替代|替换)"
---

# Component Selection

Use this skill to clarify a hardware component need, research current candidate parts, and generate a sourced CSV.

## Workflow

1. Clarify only requirements that materially change the candidate pool: circuit role, electrical limits, accuracy/performance target, interface, package/mechanical limits, temperature/compliance constraints, production-status needs, preferred vendors, and second-source policy.
2. Read `references/selection-framework.md` before defining CSV columns, scoring, source acceptance, or substitution rules.
3. Search current sources. Prefer Mouser China, Analog Devices, and TI China unless the user asks for broader coverage or these sources cannot produce enough credible candidates.
4. Use pass/fail gates first, then rank candidates by requirement match, performance, design fit, lifecycle/production status, and validation confidence.
5. Create a CSV in the working directory. Default to 10 candidate devices; if fewer credible candidates exist, output the available matches and explain the shortfall.
6. In the final response, provide the CSV path, candidate count, top 2-3 parts, key assumptions, and validation still required.

## Web Research

When web tools are available, use `WebSearch` for discovery and `WebFetch` for verification.

Search patterns:

- `site:mouser.cn <component type> <key specs> <manufacturer or interface>`
- `site:analog.com <part number> datasheet`
- `site:analog.com <component type> <key specs> datasheet`
- `site:ti.com.cn/product/cn <part number>`
- `site:ti.com.cn <component type> <key specs> datasheet`

Verification rules:

- Use manufacturer datasheets for electrical parameters.
- Use manufacturer product pages for lifecycle, package variants, design resources, and datasheet links.
- Use Mouser for discovery, orderable MPN/package clues, lifecycle/production clues, and datasheet links.
- Write only one network-address column in the CSV: `datasheet_url`.
- Do not copy search-result snippets into the CSV unless the same fact is verified from a product page or datasheet.

## CSV Requirements

Use fixed columns plus dynamic parameter columns. Fixed columns are defined in `references/selection-framework.md`.

Choose dynamic parameter columns from the component type, user requirements, and datasheet fields that matter for selection. Every hard user requirement should map to at least one CSV column. Do not use a generic template, do not use `param_` prefixes, and do not combine all specs into one `key_parameters` cell.

## Scripts

Create an empty CSV:

```bash
python scripts/new_candidate_csv.py --out candidates.csv --params channels,resolution_bits,input_range,reference,sample_rate,interface,inl,dnl,offset_error,gain_error
```

Rank a CSV that already contains manual score columns:

```bash
python scripts/score_components.py candidates.csv --out ranked.csv --weights requirement=0.35,performance=0.25,fit=0.15,lifecycle=0.15,validation=0.1
```

## Guardrails

- Do not fabricate datasheet links, lifecycle, production status, package, or parameter values. Mark unknowns explicitly.
- Do not recommend obsolete, NRND, single-source, or region-restricted parts without clearly labeling the risk.
- Do not assume footprint compatibility from package name alone; require land pattern and pinout checks.
- Do not use absolute maximum ratings as normal operating limits; apply derating and thermal review.
- For safety, mains, medical, automotive, aerospace, battery, high-current, high-voltage, or RF designs, call out applicable standards and require domain review before final release.
