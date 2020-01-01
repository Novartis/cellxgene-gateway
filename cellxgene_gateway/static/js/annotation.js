// neandertal javascript
const new_annotation_callback = (() =>{
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
    const pickn = (c, n) => n==0?'':c.substr(Math.random()*c.length,1) + pickn(c,n-1);
    const suffix = `_${pickn(chars,8)}.csv`;
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

