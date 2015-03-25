//   파일업로드 클레스 추가
nhn.husky.SE_ImageUpload = $Class({
    name : "SE_ImageUpload",
	upload_code : "",
    $init : function(oAppContainer, upload_code){
       this._assignHTMLObjects(oAppContainer);
	   this.upload_code = upload_code;
    },

    _assignHTMLObjects : function(oAppContainer){
       this.oImageUploadLayer = cssquery.getSingle("DIV.husky_seditor_imgupload_layer", oAppContainer);
    },

    $ON_MSG_APP_READY : function(){
       this.oApp.exec("REGISTER_UI_EVENT", ["imgupload", "click", "SE_TOGGLE_IMAGEUPLOAD_LAYER"]);
    },

    $ON_SE_TOGGLE_IMAGEUPLOAD_LAYER : function(){
       this.oApp.exec("TOGGLE_TOOLBAR_ACTIVE_LAYER", [this.oImageUploadLayer]);
       imgUploadFrame.location = "/image_upload/" + this.oApp.sAppId + '?code='+this.upload_code;
    }
});

function SE_RegisterCustomPlugins(oEditor, elAppContainer, upload_code){
    oEditor.registerPlugin(new nhn.husky.SE_ImageUpload(elAppContainer, upload_code));
}

