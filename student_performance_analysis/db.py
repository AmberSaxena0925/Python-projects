from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_path = Path(__file__).with_name("database.py")
_spec = spec_from_file_location("student_database_core", _path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load {_path}")
_module = module_from_spec(_spec)
_spec.loader.exec_module(_module)

add_student = _module.add_student
execute = _module.execute
initialize_database = _module.initialize_database
query_df = _module.query_df
save_performance = _module.save_performance
seed_demo_data = _module.seed_demo_data
