import os
from cellxgene_gateway import env
from cellxgene_gateway.dir_util import make_h5ad, make_annotations, annotations_suffix

def recurse_dir(path):
    if not os.path.exists(path):
        raise CellxgeneException(
            "The given path does not exist.", status.HTTP_400_BAD_REQUEST
        )

    all_entries = sorted(os.listdir(path))
    def is_h5ad(el):
        return el.endswith('.h5ad') and os.path.isfile(os.path.join(path, el))
    h5ad_entries = [x for x in all_entries if is_h5ad(x)]
    annotation_dir_entries = [x for x in all_entries if x.endswith(annotations_suffix) and make_h5ad(x) in h5ad_entries]
    def list_annotations(el):
        full_path = os.path.join(path, el)
        if not os.path.isdir(full_path):
            entries = []
        else:
            entries = [{
                "name": x[:-13] if (len(x) > 13 and x[-13] in ['-','_']) else (
                    x[:-4] if x.endswith('.csv') else x),
                "path": os.path.join(full_path, x).replace(env.cellxgene_data, ""),
            } for x in sorted(os.listdir(full_path)) if x.endswith('.csv') and os.path.isfile(os.path.join(full_path, x))]
        return [{"name":'new', "class":'new', "path":full_path.replace(env.cellxgene_data, "")}] + entries

    def make_entry(el):
        full_path = os.path.join(path, el)
        if el in h5ad_entries:
            return {
                "path": full_path.replace(env.cellxgene_data, ""),
                "name": el,
                "type": "file",
                "annotations": list_annotations(make_annotations(el)),
            }
        elif os.path.isdir(full_path) and el not in annotation_dir_entries:
            return {
                "path": full_path.replace(env.cellxgene_data, ""),
                "name": el,
                "type": "directory",
                "children": recurse_dir(full_path),
            }
        else:
            return {
                "path": full_path,
                "name": el,
                "type": "neither",
            }

    return [make_entry(x) for x in all_entries]


def render_entries(entries):
    return "<ul>" + "\n".join([render_entry(e) for e in entries]) + "</ul>"

def get_url(entry):
    return f"/view/{ entry['path'].lstrip('/') }"
def get_class(entry):
    return f" class='{entry['class']}'" if 'class' in entry else ''

def render_annotations(entry):
    if len(entry['annotations']) > 0:
        return ' | annotations: ' + ", ".join([f"<a href='{get_url(a)}'{get_class(a)}>{a['name']}</a>" for a in entry['annotations']])
    else:
        return ''

def render_entry(entry):
    if entry["type"] == "file":
        return f"<li> <a href='{ get_url(entry) }'>{entry['name']}</a> {render_annotations(entry)}</li>"
    elif entry["type"] == "directory":
        url = f"/filecrawl/{entry['path'].lstrip('/')}"
        return f"<li><a href='{url}'>{entry['name']}</a>{render_entries(entry['children'])}</li>"
    else:
        return ""
