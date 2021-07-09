

function count_all_items(){
    var el = $("[data-marker='page-title/count']");
    if (el.length == 0) {
        return false;
    }
    var str = el.text();
    var text = str.replace(/[^0-9]/g, "");
    return Number(text)
}

function count_items_in_page(){
    var el = $("[data-marker='catalog-serp']").find("[data-marker='item']");
    if (el.length == 0) {
        return false;
    }

    return el.length
}

function get_title_and_url_items(){
    var el = $("[data-marker='catalog-serp']").find("[data-marker='item']");
    if (el.length == 0) {
        return false;
    }

    var titles = [];
    var url = [];

    for (var i = 0; i < el.length; i++) {
        if (el.eq(i).find("span:contains('Показать телефон')").length > 0){
            titles.push(el.eq(i).find("[itemprop='name']").text());
            url.push('https://www.avito.ru/' + el.eq(i).find("[itemprop='url']").eq(1).attr("href"));
        }
    }

    return [titles, url];
}


function url_item(index) {
    var el = $("[data-marker='item']").eq(index).find("[itemprop='url']").eq(1);
    if (el.length == 0) {
        return false;
    }

    return 'https://www.avito.ru/' + el.attr('href');
}

function url_open(url) {
   window.open(url, 'New TAB');
   return true;
}

function click_phone() {
    var el = $("span:contains('XXX-XX-XX')");
    var el2 = $("span:contains('Без звонков')");
    if (el.length == 0) {
        if (el2.length > 0){
            return "Без звонков";
        }
        return false;
    }
    el.focus();
    el.click();

    return true;
}
function get_phone_number_base64() {
    var el = $("[data-marker='phone-popup/phone-image']");
    if (el.length == 0) {
        return false;
    }

    return el.attr("src");
}

function name(){
    var el = $("[data-marker='seller-info/name']").eq(0);
    if (el.length == 0) {
        return false;
    }

    var str = el.text();
    var name = "";
    if (str.match(/[^\s]+/)){
        name = str.replace(/(\n+)|(\s+)/g, "");
    }
    return name;
}

function last_page(){
    var el = $("[data-marker^='page(']");
    if (el.length == 0) {
        return false;
    }
    last_page = $("[data-marker^='page(']").last().attr('data-marker');
    last_page = Number(last_page.match(/\d+/)[0]);

    return last_page;
}

function next_page(page){
    var el = $("[data-marker='page("+ page +")']");
    if (el.length == 0) {
        if (page > 1){
            return next_page(page-1);
        }
        else{
            return false;
        }
    }
    el.click();
    return true;
}

function firewall_title(){
    var el_h1 = $("h1:contains('Доступ с Вашего IP')");
    var el_h2 = $("h2:contains('Доступ с Вашего IP')");
    if (el_h1.length == 0 && el_h2.length == 0) {
        return false;
    }

    return true;
}