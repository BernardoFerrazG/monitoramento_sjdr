# Street Surveillance Planning for São João del-Rei

[![CI](https://github.com/BernardoFerrazG/monitoramento_sjdr/actions/workflows/ci.yml/badge.svg)](https://github.com/BernardoFerrazG/monitoramento_sjdr/actions/workflows/ci.yml)

Where should a city install surveillance cameras so that **every street segment is watched**, using as few cameras as possible?

This project models the street network of **São João del-Rei (MG, Brazil)**, extracted from OpenStreetMap, as a graph: intersections are vertices and street segments are edges. A camera at an intersection covers every segment that touches it, so the question becomes the **minimum vertex cover** problem. That problem is NP-hard, so the project uses heuristics and measures how far they can be from the optimum.

Code and CLI messages are in Portuguese; this README is in English.

## Results

The street graph has **550 intersections and 771 street segments** ([`sjdr.gml`](sjdr.gml)).

| Method | Cameras | Proven bound vs. optimum |
| --- | --- | --- |
| Greedy + leaf rule + redundancy removal (default) | **289** | ≤ 1.07× |
| Maximal-matching 2-approximation + redundancy removal | 311 | ≤ 1.15× |
| Original greedy version of this project | 304 | ≤ 1.12× |

The bound comes from a **maximum matching** of 271 edges. Matched edges share no endpoint, so each one needs its own camera, and no cover can use fewer than 271 cameras.

## How it works

- **Leaf rule.** If an intersection has only one uncovered street left, putting the camera at the *other* end of that street is never worse, so the algorithm does that first. Dead-end streets are very common in real road networks, which makes this rule effective here.
- **Greedy step.** Otherwise, put a camera where it covers the most uncovered streets. Ties go to the intersection whose neighbours have the fewest uncovered streets left.
- **Redundancy removal.** Afterwards, any camera whose streets are all already covered by neighbouring cameras is removed.
- **2-approximation** (`--metodo emparelhamento`): take both ends of every edge of a maximal matching. This guarantees at most 2× the optimum and serves as a baseline.

## Usage

```bash
pip install -r requirements.txt
python camera_sjdr.py                       # summary
python camera_sjdr.py -d                    # + streets watched by each camera
python camera_sjdr.py -m emparelhamento     # 2-approximation baseline
python camera_sjdr.py -g other_city.gml
```

With `-d`, every camera is listed with its OpenStreetMap node id, so it can be located on the map:

```
Esquina 410707323 (openstreetmap.org/node/410707323): Rua Antônio Rocha
Esquina 3208868480 (openstreetmap.org/node/3208868480): Avenida Eduardo Magalhães, Rua Antônio Rocha, Rua Hermílio Alves
Esquina 410707589 (openstreetmap.org/node/410707589): --Rua Sem Nome 4--, Avenida Presidente Tancredo Neves, Rua José Leite de Andrade
```

## Tests

```bash
pip install pytest
pytest
```

The tests check that both methods cover every street of the city and never go below the matching lower bound. On small random graphs, they also check the solutions against the exact optimum found by brute force. CI runs them on every push.
