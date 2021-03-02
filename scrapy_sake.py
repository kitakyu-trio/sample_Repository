import scrapy
from sake.items import SakeItem

class ScrapySakeSpider(scrapy.Spider):
    name = 'scrapy_sake'
    #allowed_domains = ['https://www.saketime.jp/ranking/']
    start_urls = ['https://www.saketime.jp/ranking/']
    #start_urls = ['http://https://www.saketime.jp/ranking//']

    def parse(self, response):
        items = []
        #htmlタグのli.clearfixという場所に日本酒情報が格納されていました。
        sakes = response.css("li.clearfix")

        #ページ内にある複数あるli.clearfixの1つずつをみていく
        for sake in sakes:
            #item.pyで定義したSakeItemオブジェクトを宣言 
            item = SakeItem()
            item["prefecture_maker"] = sake.css("div.col-center p.brand_info::text").extract_first()

            #<div class="headline clearfix">のような記述の場合,headline.clearfixとして間に.をつけること
            item["brand"] = sake.css("div.headline.clearfix h2 a span::text").extract_first()

            #取得したデータのクレンジング
            if (item["prefecture_maker"] is not None) or (item["brand"] is not None):
                #¥nとスペースの削除
                item["prefecture_maker"] = item["prefecture_maker"].replace(' ','').replace('\n','')
                #prefectureとmakerの分離
                item["prefecture"] = item["prefecture_maker"].split('|')[0]
                item["maker"] = item["prefecture_maker"].split('|')[1]
                items.append(item) 
        print(items)
        
    #ページ切り替えを再起的処理で反映
        #aタグのrel="next"の要素をリンク形式で取得する
        next_page = response.css('a[rel="next"]::attr(href)').extract_first()
        if next_page is not None:
            # URLが相対パスだった場合に絶対パスに変換する
            next_page = response.urljoin(next_page)
            #yieldで1回ずつRequestを返す、リクエスト後のページでsakesが登録され、上のfor文が再度実行される
            yield scrapy.Request(next_page, callback=self.parse)
