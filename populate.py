from pathlib import Path
import shutil

DEFAULT_PATH = Path(__file__).parent
DEFAULT_PATH = DEFAULT_PATH/'..'/'SoilTemperatureModels'/'Models'
DEFAULT_PATH = DEFAULT_PATH.absolute()

def populate(path: Path):

    #cwd = Path.cwd()
    #src = cwd/'..'/'..'/'..'/'Models'
    src = path.absolute()

    dest = Path('src')/'openalea'

    # Check if the openalea package is not empty
    exclude = []
    for p in dest.iterdir():
        
        if p.is_dir():
            exclude.append(p.name)

    to_copy = []
    openalea_dirs = src.glob('*/src/openalea')
    for oa in openalea_dirs:
        for model_dir in oa.iterdir():
            model = model_dir.name
            print('Found ', model)
            if model in exclude:
                print(model ,' already exists in src/amei. Skip it!')
            else:
                print('Copy %s from %s'%(model, oa))
                to_copy.append(model)
                shutil.copytree(model_dir, dest/model)

    print('#'*80)
    if to_copy:
        print('Copied Models are', ' '.join(to_copy))
    else:
        print('Done nothing... Remove some dirs if you want to update them.')
    print('#'*80)

if __name__ == '__main__':


    if DEFAULT_PATH.exists():
        print('Using default path:', DEFAULT_PATH)
    else:
        print('Default path does not exist:', DEFAULT_PATH)
        print('Please check the path or set it manually.')
        exit(1)
    
    populate(path=DEFAULT_PATH)