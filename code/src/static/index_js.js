function render_egraph(egraph_dot) {
    d3.select("#graph").graphviz().renderDot(egraph_dot);
}

function upload() {
    let upload_input_form = document.createElement('input');
    upload_input_form.type = 'file';
    upload_input_form.onchange = _this => {
        let files = Array.from(upload_input_form.files);
        let s = Array.from(files.filter(s => (s.type.endsWith(".js"))));
        //console.log(s)
    };
    upload_input_form.click();
}

let ss = String();

async function contact_server(path, payload) {
    const url = "http://127.0.0.1:8000/" + path;
    //https://www.w3schools.com/js/js_async.asp

    const request = new Request(url, {
        method: "POST",
        body: JSON.stringify({"payload": payload}),
    });
    const response = await fetch(request);
    const s = await response.json();
    if (s['response'] === "false") {
        document.getElementById("status_div").innerHTML = "ERROR: Could not contact server.";
    }
    ss = s['response'];
}

function setStatus(status) {
    document.getElementById("status_div").innerHTML = status;
}

function create_egraph() {
    const input_text = String(document.getElementById("control_create_input").value);
    const path = "createegraph";

    contact_server(path, input_text).then(
        function(){setStatus("EGraph created.")},
        function(){setStatus("ERROR: EGraph NOT created.")}
    );

    contact_server("loadegraph", input_text).then(
        function(){setStatus("EGraph created.")},
        function(){setStatus("ERROR: EGraph NOT created.")}
    );

    render_egraph(ss) //request: Request
}
