# Component Selection Skill

Skill for electronic component selection and sourced CSV shortlist generation.

The skill helps an agent clarify hardware requirements, search preferred component sources, compare candidates, and produce a CSV containing candidate part numbers, dynamic parameter columns, production/lifecycle status, datasheet links, risks, validation notes, and ranking scores.

## What It Does

- Clarifies component-selection requirements before searching.
- Prioritizes Mouser China, Analog Devices, and TI China as research sources.
- Uses datasheets and manufacturer pages for verified electrical parameters.
- Generates CSV files with fixed base columns plus task-specific parameter columns.
- Keeps only one URL column in CSV output: `datasheet_url`.
- Includes helper scripts for creating CSV headers and ranking manually scored candidates.

## Skill Layout

```text
component-selection/
  SKILL.md
  references/
    selection-framework.md
  scripts/
    new_candidate_csv.py
    score_components.py
  examples/
    adc_8ch_12bit_example.csv
```

## Usage

Copy or install the `component-selection/` folder into your Claude Code skills directory.

Example prompts:

```text
帮我做一个 8 通道、12 bit、5V 输入范围 ADC 的元器件选型，并输出 CSV。
```

```text
Use component-selection to compare low-noise LDO candidates for a 5V to 3.3V analog rail.
```

## CSV Output

The CSV uses fixed base columns and dynamic parameter columns selected for the current component type.

Fixed columns are defined in:

```text
component-selection/references/selection-framework.md
```

For an ADC task, dynamic columns may include:

```csv
channels,resolution_bits,input_range,reference,sample_rate,interface,inl,dnl,offset_error,gain_error
```

For a MOSFET task, dynamic columns may include:

```csv
vds,id_continuous,rds_on,vgs_drive,vgs_threshold,qg,power_dissipation
```

## Helper Scripts

Create a CSV header:

```bash
python component-selection/scripts/new_candidate_csv.py --out adc_candidates.csv --params channels,resolution_bits,input_range,reference,sample_rate,interface,inl,dnl,offset_error,gain_error
```

Rank a manually scored candidate CSV:

```bash
python component-selection/scripts/score_components.py candidates.csv --out ranked.csv
```

Optional score columns:

```csv
score_requirement,score_performance,score_fit,score_lifecycle,score_validation
```

## Preferred Sources

The skill prioritizes:

- Mouser China: https://www.mouser.cn
- Analog Devices: https://www.analog.com
- TI China: https://www.ti.com.cn

Other manufacturer or distributor sources can be used when the preferred sources do not cover the requested component type well, the user requests broader coverage, or second-source comparison is required.

## License

MIT License. See [LICENSE](LICENSE).
