$(function(){
    let $li = $(".slide li");
    let $len = $li.length;
    let $points_con = $('.points');
    let $nowli = 0; // 要运动过来的幻灯片的索引值
    let $prevli = 0; // 要运动走的幻灯片的索引值
    let $prev = $('.prev');
    let $next = $('.next');
    let $timer = null; // 定时器，占个位
    let $slider = $(".slide_con")
    let $ismove = false; // 防止用户暴力操作

    
    // 除了第一张幻灯片，其他的放在右侧
    $li.not(":first").css({left:760});
    
    // 做小圆点，和幻灯片个数相同
    for(let i=0; i<$len; i++){
        let $newli = $('<li></li>');
        if(i==0){
            $newli.addClass('active');
        }
        $newli.appendTo($points_con);
    }
    
    let $points = $('.points li');

    // 小圆点点击切换
    $points.click(function(){
        $nowli = $(this).index();
        if($nowli==$prevli){
            return;
        }
        move();
        $(this).addClass('active').siblings().removeClass('active');
    })

    // 向前箭头点击切换 
    $prev.click(function(){
        // 防止用户暴力操作
        if($ismove){
            return;
        }
        $ismove = true;

        $nowli--;
        move();
        $points.eq($nowli).addClass('active').siblings().removeClass('active');
    })

    // 向后箭头点击切换
    $next.click(function(){
        // 防止用户暴力操作
        if($ismove){
            return;
        }
        $ismove = true;

        $nowli++;
        move();
        $points.eq($nowli).addClass('active').siblings().removeClass('active');
    })

    // 自动播放
    timer = setInterval(function(){
        $next.click();
        // $nowli++;
        // move();
        // $points.eq($nowli).addClass('active').siblings().removeClass('active');
    },3000);

    // 鼠标悬停时暂停
    $slider.hover(
        function(){
            clearInterval(timer);},
        function(){
            timer = setInterval(function(){
                $next.click();
            },3000);}
    )
    // $slider.mouseenter(function(){
    //     clearInterval(timer);
    // })

    // $slider.mouseleave(function(){
    //     setInterval(function(){
    //         $next.click();},3000);
    // })

    function move(){
        // 第一张幻灯片往前的时候
        if($nowli<0){
            $nowli = $len-1;
            $prevli = 0;
            $li.eq($nowli).css({'left':-760}).animate({left:0});
            // 动画执行结束后，
            $li.eq($prevli).animate({left:760},function(){$ismove = false;});
            $prevli = $nowli;
            return; //阻止下面逻辑执行
        }

        // 最后一张幻灯片往后的时候
        if($nowli>$len-1){
            $nowli = 0;
            $prevli = $len-1;
            $li.eq($nowli).css({'left':760}).animate({left:0});
            $li.eq($prevli).animate({left:-760},function(){$ismove = false;});
            $prevli = $nowli;
            return; //阻止下面逻辑执行
        }

        // 幻灯片从右边过来
        if($nowli>$prevli){
            $li.eq($nowli).css({'left':760}).animate({left:0});
            $li.eq($prevli).animate({left:-760},function(){$ismove = false;});
        }
        // 幻灯片从左边过来
        else{
            $li.eq($nowli).css({'left':-760}).animate({left:0});
            $li.eq($prevli).animate({left:760},function(){$ismove = false;});
        }
        $prevli = $nowli;
    }

    


})