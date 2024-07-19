import importlib


def create_module(name, path):
    """
    Returns module created *on the fly*. Returned module would have name same
    as given ``name`` and would contain code read from file at the given
    ``path`` (it may also be a zip or package containing *__main__* module).
    """

    spec = importlib.util.spec_from_file_location('module_name', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
