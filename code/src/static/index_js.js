function render_egraph(egraph_dot) {
    d3.select("#graph").graphviz().renderDot(egraph_dot);
}

function upload() {
    let upload_input_form = document.createElement('input');
    upload_input_form.type = 'file';
    upload_input_form.onchange = _this => {
        let files = Array.from(upload_input_form.files);
        let s = Array.from(files.filter(s => (s.type.endsWith(".json"))));
        //console.log(s)
    };
    upload_input_form.click();
}

let ss = String();

async function contact_server(path, payload, http_method) {
    const url = "http://127.0.0.1:8000/" + path;
    //https://www.w3schools.com/js/js_async.asp

    const request = new Request(url, {
        method: http_method,
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

    contact_server(path, input_text, "POST").then(
        function () {
            setStatus("EGraph created.")
        },
        function () {
            setStatus("ERROR: EGraph NOT created.")
        }
    );

    contact_server("loadegraph", input_text, "POST").then(
        function () {
            setStatus("EGraph created.")
        },
        function () {
            setStatus("ERROR: EGraph NOT created.")
        }
    );

    render_egraph(ss) //request: Request
}

function createrule() {
    const input_text1 = String(document.getElementById("rewrite_rule_create_left").value);
    const input_text2 = String(document.getElementById("rewrite_rule_create_right").value);

    contact_server2("addrule", input_text1, input_text2).then(
        function () {
            setStatus("Rule added.")
        },
        function () {
            setStatus("ERROR: Rule NOT added.")
        }
    );

}

async function contact_server2(path, payload1, payload2) {
    const url = "http://127.0.0.1:8000/" + path;
    //https://www.w3schools.com/js/js_async.asp

    const request = new Request(url, {
        method: "POST",
        body: JSON.stringify({"payload1": payload1, "payload2": payload2}),
    });
    const response = await fetch(request);
    const s = await response.json();
    if (s['response'] === "false") {
        document.getElementById("status_div").innerHTML = "ERROR: Could not contact server.";
    }
}

function render_rules() {
    // contact server, get all rules

    // const heading = document.createElement("div");
    // heading.classList.add("row");
    // const a1 = document.createElement("div");
    // const a2 = document.createElement("div");
    // a1.classList.add("col-6");
    // a2.classList.add("col");
    // const b1 = document.createElement("b");
    // const b2 = document.createElement("b");
    // b1.innerHTML = "Rule";
    // b2.innerHTML = "#";
    // a1.appendChild(b1)
    // a2.appendChild(b2)
    // heading.appendChild(a1);
    // heading.appendChild(a2);
    // document.getElementById("rr_table").appendChild(heading);
}
