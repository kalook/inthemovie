$(document).ready(function (){

    /// 섬네일 부분
    $(".resizable").each(function (item){
        if($(this).width() == 0)
        {
            $(this).load(function (){
                $(this).attr((($(this).width() / $(this).height()) > 1.75 ? "height" : "width"), "100%");
                $(this).thumbs();
            });
        }
        else
        {
            $(this).attr((($(this).width() / $(this).height()) > 1.75 ? "height" : "width"), "100%");
            $(this).thumbs();
        }
    });
    

    // 거 동영상 누를때 div팝업
    if($("a.single_vod").size() > 0)
    {
	    $("a.single_vod").fancybox({
	        'width'				: '85%',
	        'height'			: '90%',
	        'autoScale'			: false,
	        'transitionIn'		: 'none',
	        'transitionOut'		: 'none',
	        'type'				: 'iframe'
	    });
    }

    if($("a.single_vod").size() > 0)
	{
	    $("a.single_vod_swf").fancybox({
	        'width'				: '55%',
	        'height'			: '65%',
	        'autoScale'			: false,
	        'transitionIn'		: 'elastic',
	        'transitionOut'		: 'none',
	        'type'				: 'iframe'
	    });
	}
});
