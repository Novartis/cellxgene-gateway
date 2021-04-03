// neandertal javascript
// Annotations only work with file itemsources at the moment. If they work with others in the future we may need to revisit this.
const new_annotation_callback = (() =>{
    const suffix = `.csv`;
    return (e) => {
        e.preventDefault();
        const el = $(e.target);
        const href = el.attr('href');
        const base = prompt(`Name your annotations collection\nnote: the suffix "${suffix}" will be appended`);
        if (base !== null && base.length > 0) {
            if (/^[0-9a-zA-Z_]+$/.test(base)) {
                window.location = `${href}/${base}${suffix}`;
            } else {
                alert("Error: name must match ^[0-9a-zA-Z_]+$\nthat is, only numbers, letters and underscore are allowed")
            }
        }
        return false;
    }
})()

