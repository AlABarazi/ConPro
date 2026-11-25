# ConPro: simulation of interior installation work

An agent-based simulation of drywall installation work on one floor of a building, written in Python with
[Mesa](https://github.com/projectmesa/mesa) during my doctoral research at Aalto University. Plastering and painting
workers move on a grid of the floor, pick up drywall tasks zone by zone, and take breaks. The model records
utilization, idle time and task progress. It was published here in 2023 and is research code, not maintained.

## From the building model to the grid

- **The floor is a grid.** `mesa.space.MultiGrid`, sized to the CSV grid files (132 × 132 cells).
- **Walls come from the building model.** The walls and partitions were read from the building's IFC model with
  IfcOpenShell and written to grid files: `init_inner_walls.csv` (`I` marks an inner-wall cell) and
  `init_external_walls.csv`. The extraction script is not in this repository. The method is described in the ACTOR
  final report (Aalto University, 2024), section 9.1: IFC data mapped onto 0.5 m × 0.5 m cells.
- **The walkable map.** `ConPro.generat_path_file()` combines the two wall grids into `init_route.csv`.
- **Routing.** `ConPro.find_path()` finds each worker's path with A\* (`AStarFinder` from the
  [`pathfinding`](https://pypi.org/project/pathfinding/) library), so workers walk around walls, not through them.
- **Tasks.** `init_tasks_comma.csv` lists the drywall elements with their zone, dates and work per stage (frames,
  mechanical, electrical, insulation, studs, painting, finishing). `init_zones.csv` is the zone grid.
- **Worker behaviour.** `init_behavior_file.csv` gives each worker the zones it visits and how long it stays in each.
  The file in this repository is a **made-up example** in the format of the original coded site-video observations,
  so that the model runs. The original observations and the indoor-positioning data are not published.

## Known limits

- Diagonal moves use `DiagonalMovement.always`, which lets a path cut between two wall cells that touch only at a
  corner. `DiagonalMovement.only_when_no_obstacle` would prevent that.
- CSV rows run top-down and Mesa's grid bottom-up, so lookups flip y (`height - 1 - y`).
- Needs Mesa 1.x (tested with Mesa 1.2.1 on Python 3.12). Mesa 2 changed the grid and visualization APIs, and the
  model does not start under it.
- No automated tests.

## Run

```bash
pip install -r requirements.txt
python run.py        # starts Mesa's browser visualization
```

`run.py` also has single-run and batch-run modes (see the `__main__` block).

The `multiple_tasks` branch holds the later version (BIM elements as agents, several floors, indoor-positioning
input). It needs the positioning data to run, and that data is not public.

## Related publications

- Zheng, Y., Al Barazi, A., Seppänen, O., Abou-Ibrahim, H., Görsch, C. (2025). Semantic digital twin framework for
  monitoring construction workflows. *Automation in Construction* 176, 106301.
  https://doi.org/10.1016/j.autcon.2025.106301
- ACTOR: Automatic coordination of construction actors. Final report (Aalto University, 2024).

## License

Dual-licensed:

1. Open Source: GNU General Public License v3.0
2. Commercial: Available for purchase (includes additional features)

## Contact

Alan Barazi (Alaa Al Barazi), github.com/AlABarazi
