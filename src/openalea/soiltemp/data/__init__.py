try:
    import importlib_resources as resources
except ImportError:
    from importlib import resources
    

data_dir = resources.files(__name__)
