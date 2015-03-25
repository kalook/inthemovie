function resizeBoardImage(imageWidth, borderColor) {
    var target = document.getElementsByName('target_resize_image[]');
    var imageHeight = 0;
    if (target) {
        for(i=0; i<target.length; i++) { 
			
            target[i].tmp_width  = target[i].width;
            target[i].tmp_height = target[i].height;
            // 이미지 폭이 테이블 폭보다 크다면 테이블폭에 맞춘다
            if(target[i].width > imageWidth) {
                imageHeight = parseFloat(target[i].width / target[i].height)
                target[i].width = imageWidth;
                target[i].height = parseInt(imageWidth / imageHeight);
                target[i].style.cursor = 'pointer';

                // 스타일에 적용된 이미지의 폭과 높이를 삭제한다
                target[i].style.width = '';
                target[i].style.height = '';
            }

            if (borderColor) {
                target[i].style.borderWidth = '1px';
                target[i].style.borderStyle = 'solid';
                target[i].style.borderColor = borderColor;
            }
        }
    }
}

function fitImageSize(obj) {
	obj.style.display = "none";
	var image = new Image();
	var maxWidth=680;
	image.onload = function(){
	
		var width = image.width;
		var height = image.height;
		
		var scalex = maxWidth / width;
		var scaley = obj.height / height;
		
		var scale = (scalex < scaley) ? scalex : scaley;
		if (scale > 1) 
			scale = 1;
		
		obj.width = scale * width;
		obj.height = scale * height;
		
		obj.style.display = "";
	}
	image.src = obj.src;
}
