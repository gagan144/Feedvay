/**
  Copyright (C) 2017 Feedvay (Gagandeep Singh: singh.gagan144@gmail.com) - All Rights Reserved
  Content in this document can not be copied and/or distributed without the express
  permission of Gagandeep Singh.
 */

function reverse_url(base_url,replace_dict){
    for(var key in replace_dict){
        base_url = base_url.replace(key,replace_dict[key]);
    }
    return base_url;
}

// ---------- Sentencify ----------
var OPERATOR_NAMES = {
    "==":   "is equal to",
    "!=":   "is not equal to",
    "<":    "is less than",
    "<=":   "is less than equal to",
    ">":    "is greater than",
    ">=":   "is greater than equal to",
    "&&":   "and",
    "||":   "or",
    //"==null":   "is empty",
    //"!=null":   "is not empty",
};
var FUNCTIONS = {
    "startswith":   "begins with",  // 'does not' is added accordingly
    "endswith":     "ends with",    // 'does not' is added accordingly
    "includes":     "contains",     // 'does not' is added accordingly
    "indexOf":      "is in"            // 'not in' is added accordingly
}

function sentencify(code){
    /*
    This method is only for sentencing simple expressions that
        - does not contain any brackets for precedence override.
        - does not uses 'indexOf' function
        - does not include expressions withing function parameter e.g. name.startswith(('John'+'Doe'))
    */

    // Filter code
    // Remove 'data.', 'constants.', 'calculated_fields.'
    code = code.replace(/data\./g,'').replace(/constants\./g,'').replace(/calculated_fields\./g,'');

    // initialize language & lexer
    var lang_desc = lexjs.gen(lex);
    var lexer =  new lex.Lexer(lang_desc, code);

    var list_tokens = [];
    while(true) {
        var token = lexer.get_token();
        if (token === null) {
            break;
        }

        var type_name = lang_desc.type_to_string(token.type);
        if (type_name != 'WHITESPACE' && token.text!='.') {
            token["type_name"] = type_name;
            list_tokens.push(token);
        }
    }

    // make sentences
    var sentence = "";
    var flag_skip_close_bracket = false;
    var ptr = 0;
    while(ptr<list_tokens.length){
        var token = list_tokens[ptr];
        var type_name = token["type_name"];
        switch (type_name){
            case "IDENTIFIER": {
                // Check in function
                var func_name = FUNCTIONS[token.text];
                if(func_name){
                    //FUNCTION
                    sentence += '<span class="'+type_name.toLowerCase()+'">' + func_name + '</span> ';
                    ptr++; // assuming next token is '('
                    flag_skip_close_bracket = true;
                }else{
                    // IDENTIFIER
                    sentence += '<span class="'+type_name.toLowerCase()+'">' + token.text + '</span> ';
                }
            }break;
            case "OPERATOR": {
                var op = token.text;
                var op_name = OPERATOR_NAMES[op];
                if( op == ')' && flag_skip_close_bracket){
                    flag_skip_close_bracket = false;
                }
                else {
                    sentence += '<span class="' + type_name.toLowerCase() + '">' + (op_name ? op_name : op) + '</span> ';
                }
            }break;
            case "KEYWORD":{
                var keywrd = token.text;
                switch (keywrd){
                    case 'null': sentence += 'empty '; break;
                    default: sentence += keywrd;
                }
            }break;
            case "STRING":{
                sentence += '<span class="'+type_name.toLowerCase()+'">' + token.text.replace(/\'/g,'"') + '</span> ';
            }break;
            default : sentence += '<span class="'+type_name.toLowerCase()+'">' + token.text + '</span> ';
        }

        ptr++;
    }

    return {
        "html": sentence,
        "tokens": list_tokens
    };
}
// ---------- /Sentencify ----------

// ----- Summer note defaults -----
var SUMMERNOTE_CONFIG = {
    height: 150,
    toolbar: [
        ['edit',['undo','redo']],
        ['headline', ['style']],
        ['style', ['bold', 'italic', 'underline']],
        ['font', ['superscript', 'subscript', 'strikethrough', 'clear']],
        ['textsize', ['fontsize']],
        ['fontclr', ['color']],
        ['alignment', ['ul', 'ol', 'paragraph', 'lineheight']],
        ['height', ['height']],
        ['table', ['table']],
        ['insert', ['link' ,'picture','video', 'hr']],
        ['view', ['fullscreen', 'codeview']],
        ['help', ['help']]
    ]
}
// ----- /Summer note defaults -----

