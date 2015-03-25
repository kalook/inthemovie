$("document").ready(function(){
	for(i=9;i>=1;i--){
		$(".main_talk_wrap").prepend("<div class='out out_"+i+"'><p class='in'><span><a href='"+array_link[i-1]+"'>"+array[i-1]+"</a></span><span><br /><a href='"+array_link[i-1]+"'>-"+array_name[i-1]+"-	</a></span></p></div>");			
	}

	$(".out_1").mouseover(function() {
	  	$(this).addClass("over_1 over_23");
	  	$(this).css("z-index","1000");
	}).mouseout(function(){
		$(this).removeClass("over_1");
		$(this).css("z-index","10");
	});

	$(".out_2").mouseover(function() {
	  	$(this).addClass("over_2");
	   	$(this).css("z-index","1000");
	}).mouseout(function(){
	  $(this).removeClass("over_2");
	  $(this).css("z-index","10");
	});
   
	$(".out_3").mouseover(function() {
	 		$(this).addClass("over_3");
	  	$(this).css("z-index","1000");
	}).mouseout(function(){
	   $(this).removeClass("over_3");
	   $(this).css("z-index","10");
	});
   
	$(".out_4").mouseover(function() {
	 		$(this).addClass("over_4");
	  		$(this).css("z-index","1000");
	}).mouseout(function(){
		   $(this).removeClass("over_4");
		   $(this).css("z-index","10");
	});
	
	$(".out_5").mouseover(function() {
 		$(this).addClass("over_5");
  		$(this).css("z-index","1000");
	}).mouseout(function(){
	   $(this).removeClass("over_5");
	   $(this).css("z-index","10");
	});

	$(".out_6").mouseover(function() {
 		$(this).addClass("over_6");
  		$(this).css("z-index","1000");
	}).mouseout(function(){
	   $(this).removeClass("over_6");
	   $(this).css("z-index","10");
	});
	$(".out_7").mouseover(function() {
 		$(this).addClass("over_7");
  		$(this).css("z-index","1000");
	}).mouseout(function(){
	   $(this).removeClass("over_7");
	   $(this).css("z-index","10");
	});
	$(".out_8").mouseover(function() {
 		$(this).addClass("over_8");
  		$(this).css("z-index","1000");
	}).mouseout(function(){
	   $(this).removeClass("over_8");
	   $(this).css("z-index","10");
	});
	$(".out_9").mouseover(function() {
 		$(this).addClass("over_9");
  		$(this).css("z-index","1000");
	}).mouseout(function(){
	   $(this).removeClass("over_9");
	   $(this).css("z-index","10");
	});		
});