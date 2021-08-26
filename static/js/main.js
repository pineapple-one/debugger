// "use strict";

$(document).ready(function(){
    let socketio = io("/pineapple", {
        forceNew: true,
        reconnectionDelay: 100,
        reconnectionDelayMax: 500
    });

    var current_instruction = "";
    var previous_instruction = "";
    var last_instruction = "";

    $(".start, .stop, .restart").attr("disabled", true);

    socketio.emit("ports");

    socketio.on("ports_result", function(data){
        let string_ = "";
        console.log(data)
        data.ports.forEach(element => {
            string_ += '<option value="' + element + '">' + element +'</option>';
            
        });
        $("#ports").html(string_);
    });

    socketio.on("connect_confirmation", function(){
        console.log("Confirm")
        $(".connect, .refresh").attr("disabled", true);
        $(".start, .stop, .restart").attr("disabled", false);
    });

    socketio.on("vga", function(data) {
        console.log("Vga přišlo");
        $(".vga-output").attr("src", data.image);
    });

    socketio.on("source_load", function(data){
        // console.log(data.code);
        $(".src-code").html(data.code);
    });

    socketio.on("source_highlight", function(data){
        // console.log(">", current_instruction, data, current_instruction != data);
        // console.log("Data:", data[0])
        // console.log("curr ins:", current_instruction[0])
        // console.log("not eq:", current_instruction != data)
        if (current_instruction[0] != data[0])
        {
            $(".src-code").unmark();
            
            var options_first = {
                "element": "mark",
                "className": "mark-first"
            };
            var options_second = {
                "element": "mark",
                "className": "mark-second"
            };
            var options_third = {
                "element": "mark",
                "className": "mark-third"
            };
    
            last_instruction = previous_instruction;
            previous_instruction = current_instruction;
            current_instruction = data;
    
            // highlight(last_instruction, "#92e38f");
            // highlight(previous_instruction, "#e3be59");
            // highlight(current_instruction, "#c71414");
            // $(".src-code").mark(current_instruction);
            $(".src-code").markRegExp(new RegExp("\\s" + last_instruction + ":.+"), options_third);
            $(".src-code").markRegExp(new RegExp("\\s" + previous_instruction + ":.+"), options_second);
            $(".src-code").markRegExp(new RegExp("\\s" + current_instruction + ":.+"), options_first);
            // console.log(new RegExp("\\s" + current_instruction + ".+"))
    
            // console.log(last_instruction, previous_instruction, current_instruction)

        }

    });

    socketio.on("pulse_counter", function(data){
        $("#pulse-counter").text(data);
    })

    socketio.on("running", function(data){
        if(data == true){
            $("#running").addClass("btn-success");
        } else if (data == false){
            $("#running").removeClass("btn-success");
        };
    });

    socketio.on("cpu_busy", function(data){
        if(data == true){
            $("#cpu-busy").addClass("btn-warning");
        } else if (data == false){
            $("#cpu-busy").removeClass("btn-warning");
        };
    });

    socketio.on("clock", function(data){
        // console.log(data)
        if(data == true){
            $("#clock").addClass("btn-primary");
        } else if (data == false){
            $("#clock").removeClass("btn-primary");
        };
    });

    socketio.on("branch", function(data){
        if(data == true){
            $("#branch").addClass("btn-warning");
        } else if (data == false){
            $("#branch").removeClass("btn-warning");
        };
    });

    socketio.on("error", function(data){
        if(data == true){
            $("#error").addClass("btn-danger");
        } else if (data == false){
            $("#error").removeClass("btn-danger");
        };
    });

    socketio.on("u_counter", function(data){
        if (data != 0) data = data -1;
        $("#u-counter").text(data);
    });

    socketio.on("micro_codes", function(data){
        // console.log(data.micro_codes);
        let ucounter = data.u_counter;
        if (ucounter != 0) ucounter = ucounter -1;

        for (let x = 0; x < 5; x++) {
            for (let y = 0; y < 6; y++) {
                // $.each(data.micro_codes[i], function(colIndex, c){ 
                // console.log(data.micro_codes[x][y] == undefined);
                // console.log(data.micro_codes[x][y] == null);
                let codes;

                try {
                    codes = data.micro_codes[x][y];
                } catch {
                    codes = "";
                }

                $(".table-microcodes tbody tr:eq(" + y + ") td:eq(" + x + ")").text(codes);
            }
        };

        $("#ins").text(data.instruction);        
        // $.each(data.micro_codes, function(rowIndex, r){
        // $.each(r, function(colIndex, c){ 
            
        //     $(".table-microcodes tbody tr:eq(" + colIndex + ") td:eq(" + rowIndex + ")").text(c);
        
        //     });
        // });
        $(".table-microcodes tbody tr").each(function(index){
            $(this).find("td").css({"background-color": "white"});
            $(this).find("td:eq(" + ucounter + ")").css({"background-color": "yellow"});
        });
    })

    socketio.on("register_file", function(data){
        console.log(data.index, data.hex, data.bin)
        $("#bin-" + "x" + data.index).text(data.bin);
        $("#hex-" + "x" + data.index).text(data.hex);
    });

    socketio.on("bus_data", function(data){
        // console.log(data.index, data.hex, data.bin)
        $("#data-" + data.source + "-" + data.type).text(data.hex);
    });

    $(document.body).on("click", ".plus", function(){
        // console.log($(this).attr("id"))
        socketio.emit("plus_count", {plus: parseInt($(this).attr("id"))});
    });

    $(document.body).on("click", ".pulse-jump-btn", function(){
        // console.log($(this).attr("id"))
        socketio.emit("plus_count", {plus: parseInt($($("#pulse-jump")).val())});
    });

    $(document.body).on("click", ".connect", function() {  
        socketio.emit("connect_port", {port: $("#ports").val()});
    });

    $(document.body).on("click", ".refresh", function() {
        socketio.emit("ports");
    });

    $(document.body).on("click", ".ananas, .start", function() {
        socketio.emit("start", {debug: window.location.href.includes("debug")});
        $(".ananas").addClass("hidden-animation");
        setTimeout(function(){ $(".hidden").fadeIn();$(".hidden-animation").addClass("hidden").removeClass(".hidden-animation") }, 100);
    });

    $(document.body).on("click", ".stop", function() {
        $(".start, .stop, .restart").attr("disabled", true);
        $(".connect, .refresh").attr("disabled", false);
        socketio.emit("stop");
        

        $(".vga-output").fadeOut(function () {
        $(".ananas").removeClass("hidden").removeClass("hidden-animation").fadeIn("slow");
        });
    });

    $(document.body).on("click", ".restart", function() {
        socketio.emit("restart");
    });
        // highlight(["Vivamus"], "#faeb14")

});

function highlight(text, color = String, div = ".src-code"){
    
    // new HR(div, {
    //     highlight: text,
    //     backgroundColor: color
    // }).hr();

    // var context = document.querySelector(".context");
    // var instance = new Mark(context);
    // instance.mark("p,sp,-4 # 7fffc");

    // $(".src-code").mark("p,sp,-4 # 7fffc");
    // $(".src-code").markRegExp(/\s14:.+/)

    // var replace = "\s40:.+"
    // new RegExp(replace)
    // $(".src-code").markRegExp(new RegExp("\s40:.+","g"));

    // $(".src-code").unmark();
    // let text = "8";
    let re = new RegExp("\\s" + text + ":.+");
    $(div).markRegExp(new RegExp("\\s" + "cc" + ":.+"));

    $(".src-code").markRegExp(new RegExp("\\s" + "cc" + ":.+"));


    // let text = "8";
    // let re = new RegExp('\\D' + text + ':.+');

    

    
}

    