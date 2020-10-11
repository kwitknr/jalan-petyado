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

def parsePrefPage(rootP):
    lstHtl = rootP.xpath('//div[@class="result"]')
    for htl in lstHtl:
        pArea = htl.xpath('div[@class="hd-bar clearfix"]/p[@class="hd-r tx10_333"]')[0]
        htlArea = pArea.text[6:]
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
            print("\t".join([htlArea, htlName, dicSize[htlSize], txtSpa, dicPlace['プレイルーム'], pnt, cnt, 'https://www.jalan.net/' + htlID]), file=fpOut)

fpOut = open('result.txt', 'w', encoding='utf-8')
print("\t".join(['エリア', 'ホテル', 'サイズ', '温泉', 'プレイルーム', '評価', '件数', 'URL']), file=fpOut)
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
