import yaml

with open("galaxy.yml") as f:
    doc = yaml.load(f, Loader=yaml.Loader)
    version_str = doc["version"]
    if len(version_str) > 0:
        with open("version", "w") as version:
            version.write(version_str)
