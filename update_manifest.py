import json
with open("packaging/manifest.json", "r") as f:
    data = json.load(f)
if "frontend/dist" not in data["app_directories"]:
    data["app_directories"].append("frontend/dist")
with open("packaging/manifest.json", "w") as f:
    json.dump(data, f, indent=4)