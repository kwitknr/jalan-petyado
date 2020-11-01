import sys
sys.path.append('..')
from kbtool import KbGeneral
import re
import lxml.html as html

urlTop = 'https://www.jalan.net/pet/'
ptnHref = re.compile('/([^/]+)/')
dicSize = {'images/peticon_b.png':'大型犬', 
           'images/peticon_m.png':'中型犬', 
           'images/peticon_s.png':'小型犬'} 

ptnNum = re.compile('(\d+)')
def parsePrefPage(rootP):
    lstHtl = rootP.xpath('//div[@class="result"]')
    for htl in lstHtl:
        pArea = htl.xpath('div[@class="hd-bar clearfix"]/p[@class="hd-r tx10_333"]')[0]
        htlArea = pArea.text[6:]
        (htlPref, htlTown) = htlArea.split(' > ')
        lN = htl.xpath('div[@class="detail clearfix"]//p[@class="s16_33b"]/a')[0]
        htlName = lN.text
        mtch = ptnHref.match(lN.attrib['href'])
        htlID = mtch[1]
        img = htl.xpath('div[@class="detail clearfix"]//div[@class="detail-r"]/img')
        htlSize = img[0].attrib['src']

        svcSpa = htl.xpath('div[@class="detail clearfix"]//div[@class="detail-l"]/ul[@class="pet_serviceicon clear_f"]/li/img[@src="images/peticon_005.png"]')
        if svcSpa:
            txtSpa = '温泉あり'
        else:
            txtSpa = '温泉なし'
        
        dicPlace = {}
        tblPlace = htl.xpath('div[@class="detail clearfix"]//table[@class="place_table"]')[0]
        for tr in tblPlace.xpath('tr')[1:]:
            lTd = tr.xpath('td')[0:2]
            dicPlace[lTd[0].text] = lTd[1].text
        if dicPlace['客室'] == '●' and dicPlace['食堂'] == '●' and dicPlace['ロビー'] == '●':
            url = 'https://www.jalan.net/' + htlID +'/kuchikomi/'
            cont = KbGeneral.getUrl(url)
            if cont is None:
                pnt = '-'
                cnt = '-'
            else:
                rootK = html.fromstring(cont)
                lPnt = rootK.xpath('//span[@class="jlnpc-kuchikomi__point"]')
                pnt = lPnt[0].text if lPnt else '-'
                lCnt = rootK.xpath('//div[@class="jlnpc-kuchikomi__sortNav__count"]/p')
                cnt = lCnt[0].text if lCnt else '-'
            #部屋
            url = 'https://www.jalan.net/' + htlID
            cont = KbGeneral.getUrl(url)
            rootR = html.fromstring(cont)
            tbl = rootR.xpath('//table[@class="shisetsu-roomsetsubi_body"]//table')
            trs = tbl[0].xpath('tr')
            lstR = []
            if len(trs) >= 2:
                ths = trs[0].xpath('th')
                if (ths[0].text == '洋室' and ths[1].text == '和室' and
                    ths[2].text == '和洋室' and ths[3].text == 'その他' and
                    ths[4].text == '総部屋数'):
                    for td in trs[1].xpath('td'):
                        mtch = ptnNum.search(td.text)
                        r = mtch.group(1) if mtch else ''
                        lstR.append(r)
            for i in range(5-len(lstR)):
                lstR.append('-')

            
            print("\t".join([htlPref, htlTown, htlName, dicSize[htlSize], txtSpa, dicPlace['プレイルーム'], pnt, cnt] + lstR + ['https://www.jalan.net/' + htlID]), file=fpOut)

fpOut = open('result.txt', 'w', encoding='utf-8')
print("\t".join(['都道府県', 'エリア', 'ホテル', 'サイズ', '温泉', 'プレイルーム', '評価', '件数', '洋室', '和室', '和洋室', 'その他', '総部屋数', 'URL']), file=fpOut)
contTop = KbGeneral.getUrl(urlTop)
root = html.fromstring(contTop)
for lnk in root.xpath('//dd/a'):
    contP = KbGeneral.getUrl('https://www.jalan.net' + lnk.attrib['href'])
    rootP = html.fromstring(contP)
    parsePrefPage(rootP)

    lastN = rootP.xpath('//div[@class="s10_66 textright"]/a[child::span[text()="最後"]]')
    if lastN:
        baseName = lnk.attrib['href'][5:-5]
        lst = lastN[0].attrib['href']
        iLst = int(lst[len(baseName)+1:-5])
        i = 1
        while i < iLst:
            i += 1
            npath = baseName + '_' + str(i) + '.html'
            contP = KbGeneral.getUrl('https://www.jalan.net/pet/' + npath)
            rootP = html.fromstring(contP)
            parsePrefPage(rootP)

fpOut.close()
