/**
 * Created by Alexander on 2018/5/9.
 */
$(function () {



//      11 热门评论 tab的切换
        $('.hotCom_tab ul li').click(function() {
                      //当前添加active 将之前的active 移除
            $(this).siblings().removeClass('active')
            $(this).addClass('active')
            // 判断当前点击的是哪一个 然后将tab条移动到该位置
            // 289 ? 不知道什么情况,纯粹是为了凑数
            var endLeft = 0;
            var tabCount = '';
            switch($(this).html()) {
                case "人物":tabCount = 'renwu'
                    break;
                case "人生":tabCount = 'rensheng'
                    break;
                case "情感":tabCount = 'qinggan'
                    break;
                case "成长":tabCount = 'qinggan'
                    break;
                case "处世":tabCount = 'chengzhang'
                    break;
                case "视野":tabCount = 'shiye'
                    break;
                case "生活":tabCount = 'shenghuo'
                    break;
                case "智慧":tabCount = 'zhihui'
                    break;
                case "心灵":tabCount = 'xinling'
                    break;
            }
            // 清空所有数据
            $('.buyerShow .container .row').empty();
            var res_array = [];
            // 向后台请求数据 再拼接上去
            $.ajax({
                // http://localhost:8181/index
                'type':'POST',
                'url':"http://localhost:8181/meiwen",
                'data':{'cate':tabCount},
                'success':function (response,status,xhr) {
                    // 拿到返回的数据

                    res_array = response["res"];
                    for(let i = 0;i<res_array.length;i++){
                        var dict = res_array[i];
                        var j = i + 1;
                        var imgPath = dict["faceImg"];
                        var goodsBox = $('<div class="col-md-3"> <div class="showGoodsBox"> <div class="hotCom_goodsImg"><img src="" alt=""/></div><div class="hotCom_goodsInfo"><div class="hotCom_goodsUser">'+ dict["title"] +'</div><div><a class="readAll" style="padding: 5px;background-color: #3c78d8;color: white" >点击阅读全文→</a></div></div></div></div>');
                        $('.buyerShow .container .row').append(goodsBox);
                        $('.hotCom_goodsImg img').eq(i).attr('src',imgPath);
                        $('.hotCom_goodsInfo div a').eq(i).click(function () {
                                window.open('http://localhost:8181/meidetail?path='+res_array[i]['href'],'_blank');
                        });

                    }

                }
            });
















        })





})