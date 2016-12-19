var MobileAPI = {
    app_version: function(){
        return "0.0.0.0";
    },

    generateUUID : function(){
        var d = new Date().getTime();
        var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = (d + Math.random()*16)%16 | 0;
            d = Math.floor(d/16);
            return (c=='x' ? r : (r&0x3|0x8)).toString(16);
        });
        return uuid;
    },

    device_information: function(){
        //var data = {
        //    "type": "mobile_device",
        //
        //    "brand": "Test motorola",
        //    "model": "Test-XT1033",
        //    "manufacturer" : "motorola",
        //    "hardware": "qcom",
        //
        //    "platform": "Android",
        //    "os_version": "5.1",
        //    "api_sdk": "22",
        //
        //    "uuid": "TA93305MVM",
        //    "imei": "355880000000000",
        //
        //    "imsi": "40410000000000",
        //    "service_provider": "Test-Airtel",
        //    "operator_country": "in"
        //};

        var data = {
            "type": "web_client"
        }

        return JSON.stringify(data);
    },

    delete_gps: true,
    getGPS: function(max_age_sec, success_callback, error_callback){
        var lat = Math.random()*100;
        var lng = Math.random()*100;
        var timestamp = new Date().getTime();

        if(this.delete_gps){
            setTimeout(error_callback + "('Unable to get gps.')", 5*1000);
            this.delete_gps = false;
        }else{
            setTimeout(success_callback + "('gps', "+lat+", "+lng+", 200, "+timestamp+")", 5*1000);
            this.delete_gps = true;
        }
    },

    submit_response : function(context, response_dict_str){
        var TOKEN = 'test-token';

        console.log("Response Json:", response_dict_str);

        var url = null;
        if(context=='SURVEY'){
            url = '/surveys/submit-response/';
        }
        else{
            alert("Invalid form context");
            return;
        }

        $.ajax({
            type: "POST",
            //contentType: "application/json; charset=utf-8",
            url: url,
            data: {
                "token": TOKEN,
                "response": response_dict_str
            },
            //accepts: 'application/json',
            //dataType: 'json',
            success: function (result){
                alert(JSON.stringify(result));
            },
            error: function (xhr, ajaxOptions, thrownError) {
                alert('Error submitting response');
            }
        });
    },

    end_form : function(){
        document.write('Form ended!')
    },
}