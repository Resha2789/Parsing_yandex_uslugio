
function count_urls_in_page(){
    var el = $(".WorkersListBlendered-WorkerCard.Gap.Gap_bottom_l");
    if (el.length == 0) {
        return false;
    }

    return el.length
}

function get_names_urls_titles(){
    var el = $(".WorkersListBlendered-WorkerCard.Gap.Gap_bottom_l");
    if (el.length == 0) {
        return false;
    }

    var titles = [];
    var names = [];
    var urls = [];
    var href = "";
    var id = "";
    var text = "";
    for (var i = 0; i < el.length; i++) {
        id = "id_" + i;

        if (el.eq(i).find(".Link.PhoneLoader-Link").length > 0){

            names.push(el.eq(i).find(".Link.WorkerCardMini-Title").text());
            href = el.eq(i).find(".Link.WorkerCardMini-Title").attr("href").match(/(.+)[?]/)[1]
            urls.push('https://uslugi.yandex.ru' + href);

            if (el.eq(i).find(".Link.WorkerCardDescription-TextLink").length > 0){
                el.eq(i).find('.Link.WorkerCardDescription-TextLink').attr('id', id);
                document.getElementById(id).click();
                text = el.eq(i).find(".Text.Text_line_ms.Text_size_s").text();
                text = text.replace(/\n+/g, " ");

                titles.push(text);
            }
            else{
                titles.push(el.eq(i).find(".Text.Text_line_ms.Text_size_s.WorkerCardDescription-Text").text());
            }
        }
    }

    return [titles, names, urls];
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

function click_phone(index) {
    var el = $(".Link.PhoneLoader-Link").eq(index).children();
    if (el.length == 0) {
        return false;
    }
    el.focus();
    el.click();

    return true;
}

function close_phone_bar(){
    var el = $(".Modal-Content").find(".YdoIcon");
    if (el.length == 0) {
        return false;
    }
    el.click();

    return true;
}

function get_phone_number() {
    var el = $(".PhoneLoader-Phone");
    if (el.length == 0) {
        return false;
    }
    var data = el.text();
    var phone_number = 0;

    if (data.match(/\d+/)){
        phone_number = Number(data.replace(/[^\d]/g, ""));
    }
    return phone_number;
}


function check_next_page(){
    var el = $(".Pager.Serp-Pager").find("span:contains('Далее')");
    if (el.length == 0) {
        return false;
    }
    return true;
}

function get_city_array(){
    var el = $(".GeoObjectsList").find("a");
    var city_eng_array = [];
    var city_ru_array = [];
    var city_eng = "";
    var city_ru = "";

    for (var i = 0; i < el.length; i++) {
        city_eng = el.eq(i).attr("href");
        city_ru = el.eq(i).find(".Text.Text_line_m.Text_size_m").text();

        city_eng_array.push(city_eng);
        city_ru_array.push(city_ru);
    }

    return [city_eng_array, city_ru_array];
}