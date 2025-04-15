// 导航栏标记
document.addEventListener('DOMContentLoaded', function () {
    var shouye=document.querySelector('.nav').getElementsByTagName('a');
    shouye[0].style.color='#198dee';
    shouye[0].style.borderBottom='2px solid #198dee';
});

// 图片走马灯
window.addEventListener('load', function () {
    // 鼠标经过显示左右箭头
    var arrow_l = document.querySelector('.arrow-l');
    var arrow_r = document.querySelector('.arrow-r');
    var focus = document.querySelector('.pic');
    //鼠标经过
    focus.addEventListener('mouseover', function () {
        arrow_l.style.display = 'block';
        arrow_r.style.display = 'block';
        clearInterval(timer);
        timer = null;
    })
    //鼠标离开
    focus.addEventListener('mouseout', function () {
        arrow_l.style.display = 'none';
        arrow_r.style.display = 'none';
        //自动播放
        timer = setInterval(function () {
            //手动调用右侧按钮事件
            arrow_r.click();
        }, 2000);
    })

    //动态生成小圆圈
    var ul = focus.querySelector('ul');
    var ol = focus.querySelector('.circle');
    var focusWidth = focus.offsetWidth;
    //点击右侧按钮，图片滚动一张
    var num = 0;
    //circle_no控制小圆圈的播放
    var circle_no = 0;

    for (var i = 0; i < ul.children.length; i++) {
        //创建li
        var li = this.document.createElement('li');
        //记录当前小圆圈的索引号
        li.setAttribute('index', i);
        ol.appendChild(li);
        li.addEventListener('click', function () {
            for (var j = 0; j < ol.children.length; j++) {
                ol.children[j].className = '';
            }
            this.className = 'current';

            //拿到当前li的索引号
            var index = this.getAttribute('index');
            num = index;
            circle_no = index;
            //点击小圆圈，移动图片
            animate(ul, -index * focusWidth)
        })
    }
    //设置第一个小圆圈的class为current
    ol.firstElementChild.className = 'current';
    //克隆第一张图片，放到ul的最后
    var first = ul.firstElementChild.cloneNode(true);
    ul.appendChild(first);

    //右侧按钮
    arrow_r.addEventListener('click', function () {
        //如果走到了最后复制的一张图片，ul需要快速复原，让left为0
        if (num === ul.children.length - 1) {
            ul.style.left = 0;
            num = 0;
        }
        num++;
        animate(ul, -num * focusWidth);
        circle_no++;
        //如果circle_no走到最后，需要复原
        if (circle_no === ol.children.length) {
            circle_no = 0;
        }
        //清除其余小圆圈的current类名
        for (var i = 0; i < ol.children.length; i++) {
            ol.children[i].className = '';
        }
        //设置当前小圆圈的current
        ol.children[circle_no].className = 'current';
    });
    //左侧按钮
    arrow_l.addEventListener('click', function () {
        //如果走到了最后复制的一张图片，ul需要快速复原，让left为0
        if (num === 0) {
            num = ul.children.length - 1;
            ul.style.left = -num * focusWidth + 'px';
        }
        num--;
        animate(ul, -num * focusWidth);
        circle_no--;
        //如果circle_no走到最后，需要复原
        if (circle_no === -1) {
            circle_no = ol.children.length - 1;
        }
        //清除其余小圆圈的current类名
        for (var i = 0; i < ol.children.length; i++) {
            ol.children[i].className = '';
        }
        //设置当前小圆圈的current
        ol.children[circle_no].className = 'current';
    });
    //自动播放
    var timer = setInterval(function () {
        //手动调用右侧按钮事件
        arrow_r.click();
    }, 1800);
});