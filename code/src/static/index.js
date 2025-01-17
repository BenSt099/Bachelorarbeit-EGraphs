/**
 * This file includes all functions that are necessary for index.html and
 * egraph.html to operate properly. The following functions are available:
 *
 * - contactServer(path, payload, httpMethod)
 * - renderEGraph(egraph)
 * - addMessageToStatusBar(status, msg)
 * -
 * - loadEGraph()
 * - exportEGraph()
 * - extractBestTerm()
 * - displayExtractedBestTerm(term)
 * - createRewriteRule(lhs, rhs)
 * - displayRewriteRule(lhs, rhs, num)
 * - applyRewriteRule(number)
 * - uploadRewriteRules()
 * - downloadRewriteRules()
 * - moveThroughDebugOutput(direction)
 * - uploadSession()
 * - downloadSession()
 *
 */

/**
 * Contacts the server and returns the result.
 * @param {string} path - The destination path.
 * @param {string} payload - Data in JSON format.
 * @param {string} httpMethod - Either GET or POST.
 * @returns {json} Data retrieved from the server in JSON format.
 */
async function contactServer(path, payload, httpMethod) {
    let request;
    if (payload == null) {
        request = new Request("http://127.0.0.1:8000" + path, {
            method: httpMethod
        });
    } else {
        request = new Request("http://127.0.0.1:8000" + path, {
            method: httpMethod,
            body: payload,
        });
    }
    return (await fetch(request)).json();
}


/**
 * Renders an EGraph from an input string in DOT format.
 * @param {string} egraph - The EGraph in DOT format.
 */
function renderEGraph(egraph) {
    d3.select("#graph").graphviz().renderDot(egraph);
}


/**
 * Adds a message to the status bar.
 * @param {string} status - One of the following: [INFO], [ERROR], [WARN]
 * @param {string} msg - The actual message that should be displayed.
 */
function addMessageToStatusBar(status, msg) {
    let rowDiv = document.createElement("div");
    let statusDiv = document.createElement("div");
    let msgDiv = document.createElement("div");
    rowDiv.className = "row";
    rowDiv.style.margin = "5px";
    rowDiv.style.padding = "5px";
    rowDiv.style.border = "1.5px solid black";
    rowDiv.style.borderRadius = "6px";
    statusDiv.style.fontWeight = "bold";
    statusDiv.className = "col-4";
    msgDiv.style.fontWeight = "bold";
    msgDiv.className = "col-12";
    if (status === "[ERROR]") {
        statusDiv.style.color = "#b40808";
        rowDiv.style.backgroundColor = "#e39b9b";
    } else if (status === "[INFO]") {
        statusDiv.style.color = "#077c7c";
        rowDiv.style.backgroundColor = "#9be3e3";
    } else {
        statusDiv.style.color = "#c47011";
        rowDiv.style.backgroundColor = "#ffc88e";
    }
    statusDiv.innerHTML = status;
    msgDiv.innerHTML = msg;
    msgDiv.style.paddingRight = "0px";
    rowDiv.appendChild(statusDiv);
    rowDiv.appendChild(msgDiv);
    document.getElementById("status_msg").appendChild(rowDiv);
    document.getElementById("status_msg").scrollTop = document.getElementById("status_msg").scrollHeight;
}


function create() {
    if (String(document.getElementById("control_create_input").value) === "") {
        return;
    }
    contactServer("/loadegraph", null, "GET").then(
        function (value) {
            if (value['response'] !== "false") {
                if (confirm("There is already an EGraph. Do you want to replace it and all data attached to it?") === true) {
                    addMessageToStatusBar("[INFO]", "Creating new EGraph...");
                    for (const child of document.getElementById("rr_table").children) {
                        document.getElementById("rr_table").removeChild(child);
                    }
                    createEGraph();
                } else {
                    addMessageToStatusBar("[INFO]", "Action aborted.");
                }
            } else {
                createEGraph();
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.")
        });
}


function createEGraph() {
    contactServer("/createegraph",
        JSON.stringify({
            "payload": String(document.getElementById("control_create_input").value)
        }),
        "POST").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT create EGraph.");
            } else {
                addMessageToStatusBar("[INFO]", "EGraph created.");
                document.getElementById("control_create_input").value = "";
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
        });
    loadEGraph();
    document.getElementById("control_create_input").value = "";
    createRewriteRule("(* x 2)", "(<< x 1)");
    createRewriteRule("(/ x x)", "(1)");
}


/**
 * Loads the currently selected EGraph.
 */
function loadEGraph() {
    contactServer("/loadegraph", null, "GET").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT load EGraph.");
            } else {
                renderEGraph(value['p2'])
                addMessageToStatusBar("[INFO]", "EGraph loaded.");
                addMessageToStatusBar("[INFO]", value['p1'])
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.")
        });
}


/**
 * Orders server to export the current EGraph into the selected format.
 */
function exportEGraph() {
    let format;
    if (document.getElementById("export_pdf").checked) {
        format = String("pdf")
    } else if (document.getElementById("export_svg").checked) {
        format = String("svg")
    } else {
        format = String("png")
    }
    contactServer("/exportegraph",
        JSON.stringify({"payload": format}), "POST").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT export EGraph.");
            } else {
                addMessageToStatusBar("[INFO]", "EGraph exported to " + value['response']);
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
        });
}


function extractBestTerm() {
    contactServer("/extractterm", null, "POST").then(function (value) {
        if (value['response'] === "false") {
            addMessageToStatusBar("[WARN]", "Could NOT extract term.");
        } else {
            addMessageToStatusBar("[INFO]", "Extracted term.");
            displayExtractedBestTerm(value['response']);
        }
    }, function (error) {
        addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
    });
}


/**
 * Displays the extracted term in the intended div-element.
 * @param {string} term - The extracted term
 */
function displayExtractedBestTerm(term) {
    document.getElementById("term").innerHTML = term;
}


/**
 * Creates a Rewrite Rule.
 * @param {string} lhs - Left-hand side of the rewrite rule
 * @param {string} rhs - Right-hand side of the rewrite rule
 */
function createRewriteRule(lhs, rhs) {
    let left;
    let right;
    if (lhs === "" && rhs === "") {
        left = String(document.getElementById("rewrite_rule_create_left").value)
        right = String(document.getElementById("rewrite_rule_create_right").value)
    } else {
        left = String(lhs);
        right = String(rhs);
    }
    if (left === "" || right === "") {
        return;
    }
    contactServer("/addrule", JSON.stringify({
        "payload": "rule", "lhs": left, "rhs": right
    }), "POST").then(function (value) {
        if (value['response'] === "false") {
            addMessageToStatusBar("[WARN]", "Could NOT create Rule.");
        } else {
            addMessageToStatusBar("[INFO]", "Rule created.");
            displayRewriteRule(left, right, value['response']);
        }
    }, function (error) {
        addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
    });
}


/**
 * Displays a given Rewrite Rule.
 * @param {string} lhs - Left-hand side of the rewrite rule
 * @param {string} rhs - Right-hand side of the rewrite rule
 * @param {string} num - The number of the given rewrite rule.
 */
function displayRewriteRule(lhs, rhs, num) {
    const heading = document.createElement("div");
    const button = document.createElement("button");
    button.innerHTML = "Apply";
    button.type = "button";
    button.classList.add("btn", "btn-success", "btn-sm");
    button.id = "ar" + String(num);
    button.style.marginLeft = "10px";
    button.setAttribute("onclick", "applyRewriteRule(" + num + ")");
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


/**
 * Applies the Rewrite Rule that is registered under a certain number.
 * @param {string} number - Number of the rewrite rule.
 */
function applyRewriteRule(number) {
    contactServer("/applyrule",
        JSON.stringify({"payload": number}), "POST").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT apply rule to EGraph.");
            } else {
                addMessageToStatusBar("[INFO]", "Applied rule.");
                document.getElementById("ar" + String(number)).innerHTML = "Applied";
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
        });
}


function loadRewriteRules() {
    contactServer("/getrules",
        null, "GET").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT load rewrite rules.");
            } else {
                addMessageToStatusBar("[INFO]", "Loaded rules.");
                for (const child of document.getElementById("rr_table").children) {
                    document.getElementById("rr_table").removeChild(child);
                }
                const data = JSON.parse(JSON.stringify(value['p1']));
                for (const item of Object.keys(data)) {
                    displayRewriteRule(data[item][1], data[item][2], data[item][0]);
                }
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
        });
}


function uploadRewriteRules() {
    let upload_input_form = document.createElement('input');
    upload_input_form.type = 'file';
    upload_input_form.onchange = _this => {
        let files = Array.from(upload_input_form.files);
        let s = Array.from(files.filter(s => (s.type === "application/json")));
        let t = s.at(0);
        let reader = new FileReader();
        reader.readAsText(t);
        reader.onload = function () {
            try {
                contactServer("/uploadrules", JSON.stringify({
                    "payload": "rule", "p1": reader.result.trim()
                }), "POST").then(function (value) {
                    if (value['response'] === "false") {
                        addMessageToStatusBar("[WARN]", "Could NOT upload file.");
                    } else {
                        addMessageToStatusBar("[INFO]", "Uploaded file.");
                        loadRewriteRules();
                    }
                }, function (error) {
                    addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
                });
            } catch (error) {
                addMessageToStatusBar("[ERROR]", "File could not be parsed.");
            }
        };
    };
    upload_input_form.click();
}


function downloadRewriteRules() {
    contactServer("/downloadrules", null, "POST").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT download rules.");
            } else {
                addMessageToStatusBar("[INFO]", "Downloaded rules.");
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
        });
}


/**
 * Moves through debug output and displays the new state of the EGraph.
 * @param {string} direction - Tells the server in which direction to move
 * (forward, backward, fastforward, fastbackward).
 */
function moveThroughDebugOutput(direction) {
    contactServer("/move", JSON.stringify({
        "payload": direction,
        "p1": String(document.getElementById("mode_debug").checked)
    }), "POST").then(function (value) {
        if (value['response'] === "false") {
            addMessageToStatusBar("[WARN]", "Could NOT load debug output - switch from standard to debug mode?");
        } else {
            addMessageToStatusBar("[INFO]", direction + ".");
        }
    }, function (error) {
        addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
    });
    loadEGraph();
}


function uploadSession() {
    let upload_input_form = document.createElement('input');
    upload_input_form.type = 'file';
    upload_input_form.onchange = _this => {
        let files = Array.from(upload_input_form.files);
        let s = Array.from(files.filter(s => (s.type === "application/json")));
        let t = s.at(0);
        let reader = new FileReader();
        reader.readAsText(t);
        reader.onload = function () {
            try {
                contactServer("/loadfromfile", JSON.stringify({
                    "payload": "rule", "p1": reader.result.trim()
                }), "POST").then(function (value) {
                    if (value['response'] === "false") {
                        addMessageToStatusBar("[WARN]", "Could NOT upload file.");
                    } else {
                        addMessageToStatusBar("[INFO]", "Uploaded file. Loaded EGraph.");
                    }
                }, function (error) {
                    addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
                });
            } catch (error) {
                addMessageToStatusBar("[ERROR]", "File could not be parsed.");
            }
        };
    };
    upload_input_form.click();
}


function downloadSession() {
    contactServer("/savetofile", null, "POST").then(
        function (value) {
            if (value['response'] === "false") {
                addMessageToStatusBar("[WARN]", "Could NOT download session.");
            } else {
                addMessageToStatusBar("[INFO]", "Downloaded session.");
            }
        }, function (error) {
            addMessageToStatusBar("[ERROR]", "Could NOT contact server.");
        });
}


function loadData() {
    loadEGraph();
    loadRewriteRules();
}
