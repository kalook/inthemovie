//{
/**
 * @fileOverview This file contains Husky plugin that takes care of the operations related to changing the lineheight using Select element
 * @name hp_SE_LineHeightWithSelectUI.js
 */
nhn.husky.SE_LineHeightWithSelectUI = $Class({
	name : "SE_LineHeightWithSelectUI",

	_assignHTMLObjects : function(elAppContainer){
		this.elLineHeightSelect = cssquery.getSingle("SELECT.husky_seditor_ui_lineHeight_select", elAppContainer);
	},
	
	$ON_MSG_APP_READY : function(){
		this.oApp.registerBrowserEvent(this.elLineHeightSelect, "change", "SET_LINEHEIGHT_FROM_SELECT_UI");
		this.elLineHeightSelect.selectedIndex = 0;
	},
	
	$ON_MSG_STYLE_CHANGED : function(sAttributeName, sAttributeValue){
		if(sAttributeName == "lineHeight"){
			this.elLineHeightSelect.value = sAttributeValue;
			if(this.elLineHeightSelect.selectedIndex < 0) this.elLineHeightSelect.selectedIndex = 0;
		}
	},

	$ON_SET_LINEHEIGHT_FROM_SELECT_UI : function(){
		var nLineHeight = this.elLineHeightSelect.value;
		if(!nLineHeight) return;

		this.elLineHeightSelect.selectedIndex = 0;
		this.oApp.exec("SET_LINEHEIGHT", [nLineHeight]);
		this.oApp.exec("CHECK_STYLE_CHANGE", []);
	}
}).extend(nhn.husky.SE_LineHeight);
//}