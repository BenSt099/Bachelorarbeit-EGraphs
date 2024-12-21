async function contact_server(path, payload, http_method) {
    let request;
    if (payload == null) {
        request = new Request("http://127.0.0.1:8000" + path, {
            method: http_method
        });
    } else {
        request = new Request("http://127.0.0.1:8000" + path, {
            method: http_method,
            body: payload
        });
    }
    return (await fetch(request)).json();
}

//https://www.w3schools.com/js/js_async.asp
//// body: JSON.stringify({"payload": payload}),
// const response = await fetch(request);
// return await response.json();
// if (s['response'] === "false") {
//     document.getElementById("status_div").innerHTML = "ERROR: Could not contact server.";
// }
// ss = s['response'];

function render_egraph(egraph_in_dot) {
    d3.select("#graph").graphviz().renderDot(egraph_in_dot);
}

function add_to_status(status, msg) {
    let row = document.createElement("div");
    let status_p = document.createElement("div");
    let msg_p = document.createElement("div");
    row.className = "row";
    status_p.style.fontWeight = "bold";
    status_p.className = "col-3";
    msg_p.style.fontWeight = "bold";
    msg_p.className = "col-7";
    if (status === "[ERROR]") {
        status_p.style.color = "#b40808";
    } else if (status === "[INFO]") {
        status_p.style.color = "#077c7c";
    } else {
        status_p.style.color = "#c47011";
    }
    status_p.innerHTML = status;
    msg_p.innerHTML = msg;
    msg_p.style.paddingRight = "0px";
    row.appendChild(status_p);
    row.appendChild(msg_p);
    document.getElementById("status_msg").appendChild(row);
    document.getElementById("status_msg").scrollTop = document.getElementById("status_msg").scrollHeight;
}

function set_extracted_term(term) {
    document.getElementById("term").innerHTML = term;
}

function create_egraph() {
    contact_server("/createegraph",
        JSON.stringify({"payload": String(document.getElementById("control_create_input").value)}),
        "POST").then(
        function (value) {
            if (value['response'] === "false") {
                add_to_status("[WARN]", "Could NOT create EGraph.");
            } else {
                add_to_status("[INFO]", "EGraph created.");
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.");
        }
    );
    contact_server("/loadegraph", null, "GET").then(
        function (value) {
            if (value['response'] === "false") {
                add_to_status("[WARN]", "Could NOT load EGraph.");
            } else {
                render_egraph(value['response'])
                add_to_status("[INFO]", "EGraph loaded.");
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.")
        }
    );
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


function create_rule() {
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
