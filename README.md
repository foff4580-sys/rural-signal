# Rural Signal

Rural Signal is a local, text-first demonstration that turns scattered rural
safety notices into plain-language action cards without hiding source status or
allowing unverified reports to present themselves as official.

![Official flash-flood case](demo/01-official-flash-flood.jpg)

## What the contest edition proves

- Spark-X2.6-4B performs useful local interpretation on four synthetic cases.
- Ordinary application code owns the incident, location, time, source, and
  trust status.
- Spark writes the concise summary, chooses only from bounded action and
  unknown lists, and creates a 160-character-or-shorter SMS preview.
- A deterministic validator withholds failed model output.
- An adversarial forwarded-text case cannot promote an unverified report to
  official or confirmed status.

![Adversarial unverified case](demo/02-adversarial-unverified.jpg)

## Reproduce

Requirements:

- Python 3.12 or later
- `llama.cpp` build 11838 or a compatible later build
- The official `XHToken/Spark-X2.6-4B-GGUF`
  `Spark-X2.6-4B-Q4_K_M.gguf` model

The recorded run used:

- model repository revision
  `fe31f8d64890302cc3a1d365d700357b4b75ba77`
- model SHA-256
  `91cb2811aebb47ac916aa619d27d4cdd7f4143106b7917accb8ead4cd7f5cbd9`
- llama.cpp 0.7.0-dev, build 11838, commit `4231b23dc`
- Linux x86-64 on an Intel Core Ultra 7 255H, CPU inference, 8 threads
- Q4_K_M quantization, 4096-token context, temperature 0, reasoning disabled,
  320 output-token limit, single-turn mode

Set the two runtime paths:

```bash
export RURAL_SIGNAL_LLAMA=/path/to/llama-cli
export RURAL_SIGNAL_MODEL=/path/to/Spark-X2.6-4B-Q4_K_M.gguf
```

Run the checks and application:

```bash
python3 test_engine.py
python3 verify_package.py
python3 engine.py --all
python3 app.py
```

Then open `http://127.0.0.1:8787/`.

## Safety boundary

All bundled cases and locations are synthetic. Rural Signal contacts no agency,
sends no SMS, and is not an emergency service. It does not replace official
alerts, emergency instructions, or human judgment. The four-case evaluation is
evidence for these exact demonstrations, not a claim of universal safety.

## Licenses

- Rural Signal source code: MIT, see [LICENSE](LICENSE).
- Spark-X2.6-4B and the official GGUF repository: Apache-2.0.
- llama.cpp: MIT.

Model weights and llama.cpp binaries are not redistributed in this repository.
