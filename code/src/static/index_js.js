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


function create() {
    contact_server("/loadegraph", null, "GET").then(
        function (value) {
            if (value['response'] !== "false") {
                if (confirm("There is already an EGraph. Do you want to replace it and all data attached to it?") === true) {
                    add_to_status("[INFO]", "Creating new EGraph...");
                    create_egraph();
                } else {
                    add_to_status("[INFO]", "Action aborted.");
                }
            } else {
                create_egraph();
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.")
        }
    );
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
                document.getElementById("control_create_input").value = "";
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.");
        }
    );
    loadegraph();
    document.getElementById("control_create_input").value = "";
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
    contact_server("/addrule",
        JSON.stringify({
            "payload": "rule",
            "lhs": String(document.getElementById("rewrite_rule_create_left").value),
            "rhs": String(document.getElementById("rewrite_rule_create_right").value)
        }),
        "POST").then(
        function (value) {
            if (value['response'] === "false") {
                add_to_status("[WARN]", "Could NOT create Rule.");
            } else {
                add_to_status("[INFO]", "Rule created.");
                render_rule(String(document.getElementById("rewrite_rule_create_left").value),
                    String(document.getElementById("rewrite_rule_create_right").value),
                    value['response']);
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.");
        }
    );
}


function render_rule(lhs, rhs, num) {
    const heading = document.createElement("div");
    const button = document.createElement("button");
    button.innerHTML = "Apply";
    button.type = "button";
    button.classList.add("btn", "btn-success", "btn-sm");
    button.style.marginLeft = "10px";
    button.setAttribute("onclick", "apply_rule(" + num + ")");
    heading.classList.add("row");
    heading.style.marginBottom = "5px";
    const a1 = document.createElement("div");
    const a2 = document.createElement("div");
    a1.classList.add("col-6");
    a2.classList.add("col");
    const b1 = document.createElement("b");
    const b2 = document.createElement("b");
    b1.innerHTML = lhs + " => " + rhs;
    b2.innerHTML = num;
    a1.appendChild(b1);
    a2.appendChild(b2);
    a2.appendChild(button);
    heading.appendChild(a1);
    heading.appendChild(a2);
    document.getElementById("rr_table").appendChild(heading);
    document.getElementById("rewrite_rule_create_left").value = "";
    document.getElementById("rewrite_rule_create_right").value = "";
}


function apply_rule(number) {
    contact_server("/applyrule",
        JSON.stringify({"payload": number}),
        "POST").then(
        function (value) {
            if (value['response'] === "false") {
                add_to_status("[WARN]", "Could NOT apply rule to EGraph.");
            } else {
                add_to_status("[INFO]", "Applied rule.");
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.");
        }
    );
}


function move_in_debug_info(way) {
    contact_server("/move",
        JSON.stringify({
            "payload": way,
            "p1": String(document.getElementById("mode_debug").checked)
        }),
        "POST").then(
        function (value) {
            if (value['response'] === "false") {
                add_to_status("[WARN]", "Could NOT move in debug information.");
            } else {
                add_to_status("[INFO]", way + ".");
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.");
        }
    );
    loadegraph();
}


function loadegraph() {
    contact_server("/loadegraph", null, "GET").then(
        function (value) {
            if (value['response'] === "false") {
                add_to_status("[WARN]", "Could NOT load EGraph.");
            } else {
                render_egraph(value['p2'])
                add_to_status("[INFO]", "EGraph loaded.");
                add_to_status("[INFO]", value['p1'])
            }
        },
        function (error) {
            add_to_status("[ERROR]", "Could NOT contact server.")
        }
    );
}
