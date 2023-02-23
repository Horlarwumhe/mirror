import requests
from lxml import html
ses = requests.Session()
from pathlib import Path
# import urllib.parse as parse
import os
import urllib.parse
headers={'User-Agent':'''Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/11.1 Safari/605.1.15''',
    "Accept":"text/html,image/png,image/jpeg,image/pjpeg,image/x-xbitmap,image/svg+xml,image/gif;q=0.9,*/*;q=0.1"}
path = 'classcentral'
domain = 'https://www.classcentral.com'
# os.mkdir(path)
found = []
def main():
    # global
    print('downloading base page')
    url = domain
    r = ses.get(domain,headers=headers,proxies={'htt':'socks5://localhost:9050'})
    print(r.url)
    src = r.text
    with open('index.html','w') as f:
        f.write(src)
    print('downloaded...')
    doc = html.fromstring(src)
    assets = [el for el in doc.xpath('//*') if el.tag in ('script','img','link')]
    urls = []
    for el in assets:
        if el.tag in ('img','script'):
            key = 'src'
        if el.tag == 'link':
            key = 'href'
        u = el.get(key)
        if isinstance(u,bytes):
            u = u.decode()
        netloc = urllib.parse.urlparse(u).netloc
        if isinstance(netloc,bytes):
            netloc = netloc.decode()
        if netloc and netloc not in domain:
            continue
        if not u:
            continue
        if not netloc:
            u = domain+'/'+u.lstrip('/')
        urls.append(u)
    download_assets(urllib.parse.urlparse(r.url).path,urls)
    links = doc.xpath('//a')
    pages = []
    for link in links:
        link = link.get('href')
        print('href ---------',link)
        if not link.strip() or link.startswith('#'):
            print('target link')
            continue
        netloc = urllib.parse.urlparse(link).netloc
        if netloc and netloc not in domain:
            print('dont crawl third party urls',link)
            continue
        link = norm_path(urllib.parse.urlparse(r.url).path,link)
        p = urllib.parse.urlparse(link).netloc
        pages.append(link)
    for link in pages:
        crawl_page(link)
        # print(link)
    # # print('assets----------')
    # for a in urls:
    #     print(a)

def exclude(page):
    x = [
    '/subject/[^cs]'
    '/subjects/[^business]'
    '/report/'


    ]

def crawl_page(page,dest=None):
    print('crawling page ',page)
    if exclude(page):
        print('exclude ',page)
    page = page.strip()
    px = Path(urllib.parse.urlparse(page).path.lstrip('/'))
    if px.exists():
        # print('page exists ',page)
        pass
    page = page.split('#')[0]
    if page in found:
        print('found ',page)
        return
    if '/report/' in page:
        while 1:
            s = input('scrap this page %s'%page)
            if s == 'n':
                return
            if s == 'y':
                break
    elif '/subject/cs' in page or '/subject/bus' in page:
        print('special subjects')
    elif '/subjectzs/' in page:
        print('ignore subjects',page)
        return
    if urllib.parse.urlparse(page).path == '/':
        return
    try:
        r = ses.get(page,headers=headers,proxies={'http':'socks5://localhost:9050'})
    except:
        raise
    if r.status_code != 200:
        print('hoop',r)
        return
    doc = html.fromstring(r.content)
    assets = [el for el in doc.xpath('//*') if el.tag in ('script','img','link')]
    urls = []
    for el in assets:
        if el.tag in ('img','script'):
            key = 'src'
        if el.tag == 'link':
            key = 'href'
        u = el.get(key)
        if isinstance(u,bytes):
            u = u.decode()
        # print(u.__class__)
        netloc = urllib.parse.urlparse(u).netloc
        if isinstance(netloc,bytes):
            netloc = netloc.decode()
        # print(netloc.__class__,u.__class__)
        if netloc and netloc not in domain:
            # print('assets not in same domain',u,netloc)
            continue
        if not u:
            continue
        if not netloc:
            u = domain+'/'+u.lstrip('/')
        urls.append(u)
    import pdb
    pdb.set_trace()
    path = Path(urllib.parse.urlparse(r.url).path.lstrip('/').rstrip('/')+'.html')
    print(path)
    try:
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_bytes(r.content)
    except Exception as e:
        print(e,' hhopp sss ')
    import pdb
    # pdb.set_trace()
    found.append(page)
    download_assets(urllib.parse.urlparse(r.url).path,urls)

def norm_path(base,path):
    # path = urllib.parse.urlparse()
    if 'http' in path[:6]:
        return path
        # return f"{domain}/{path.lstrip('/')}"
    if path.startswith('//'):
        path = f"https:{path}"
    elif path.startswith('/'):
        path = f"{domain}/{path.lstrip('/')}"
    elif 'http' not in path[:6]:
        # print(domain,base,path,'----')
        path = f"{domain}/{base.strip('/')}/{path}"
    return path
assets = []
def download_assets(base_path,urls):
    print('downloading page assets',base_path)
    for url in urls:
        print('downloading assets for ',url)
        if url in assets:
            print('asset downloaded')
            continue
        url = url.strip()
        url = norm_path(base_path,url)
        path = urllib.parse.urlparse(url).path.lstrip('/')
        if os.path.exists(path):
            print('path exists',path,' ',url)
            continue
        r = ses.get(url,headers=headers,proxies={'http':'socks5://localhost:9050'})
        path = Path(path)
        # print('mkdir ',path.parent,' write_bytes ',path   
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_bytes(r.content)
        except Exception as e:
            print('error write_bytes ',e)
        assets.append(url)


def fix_links(src,abs_path):
    print('fix_links')
    # raise
    h = html.fromstring(src.encode())
    links = [el for el in h.xpath('//*') if el.tag in ('a','script','img','link')]
    for link in links:
        if link.tag in ('img','script'):
            key = 'src'
        if link.tag in ('link','a'):
            key = 'href'
        href = link.get(key)
        if not href:
            continue
        if "category/best-courses" in href:
            # import pdb
            pass
        p = urllib.parse.urlparse(href)
        if 'classcentral.com' in p.netloc:
            if not p.path:
                path = '/'
            else:
                path = p.path
            link.attrib[key] = path.rstrip('/').strip()
        elif not p.netloc and p.path.startswith('/'):
            link.attrib[key] = link.attrib[key].rstrip('/').strip()
            pass
        elif p.netloc:
            # print('third party site ',href, 'on ',abs_path)
            pass
        # if '/about' in href:
        #     import pbd
        #     pdb.set_trace()
        print(href,' ----> ',link.attrib[key])
        if link.attrib[key] in ('/abou',):
            print('fixing ',href,' on ',abs_path)
            link.attrib[key] = '/about'
            print(' new ',link.attrib[key])
    src = html.tostring(h)
    with open(abs_path,'wb') as f:
        f.write(src)
# f = open('./report/2022-year-in-review.html').read()
# fix_links(f,'./report/2022-year-in-review.html')

def norm(base_path,urls):
    for u in urls:
        print(norm_path(base_path,u),u)

s = ['/',('/q/w/e/','/y/t/mk','//sq/s/q/','ba/de/pi','aqw/hue/lka.mp4/')]

crawl_page("https://www.classcentral.com/catalog-iframe?a={%22courseName%22%3A%221000s%20of%20Free%20Certificates%22%2C%22courseUrl%22%3A%22https%3A\%2F\%2Fwww.classcentral.com\%2Freport\%2Ffree-certificates\%2F%22%2C%22imageUrl%22%3A%22https%3A\%2F\%2Fwww.classcentral.com\%2Freport\%2Fwp-content\%2Fuploads\%2F2021\%2F12\%2Ffree-certificates-banner.png%22%2C%22providerName%22%3A%22Class%20Central%22%2C%22summary%22%3A%221000s%20of%20courses%20with%20free%20certificates%20and%20badges%20from%20universities%2C%20companies%2C%20and%20nonprofits%20worldwide.%22%2C%22institutionLogo%22%3A%22\%2Flogos\%2Fproviders\%2Fclass-central-hz.png%22%2C%22institutionName%22%3A%22Class%20Central%22%2C%22frequency%22%3A2%2C%22tableId%22%3A%22institutiontable%22%2C%22subjects%22%3A[]}")
f = open('./catalog-iframe.html').read()
fix_links(f,'./catalog-iframe.html')


