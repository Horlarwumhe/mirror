from lxml import html
import os
import urllib.parse


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
        if link.attrib[key] in ('/abou',):
            print('fixing ',href,' on ',abs_path)
            link.attrib[key] = '/about'
            print(' new ',link.attrib[key])
    src = html.tostring(h)
    with open(abs_path,'wb') as f:
        f.write(src)
        
            
    # raise



# walk =
# import pdb
    # pdb.set_trace()
Files = []
def main():
    for path,_,files in os.walk('.'):
        for file in files:
            abs_path = os.path.join(path,file)
            if os.path.splitext(abs_path)[1] in ('.svg','.hi','.jpeg','.js','.css','.png','.jpg','.woff2'):
                continue
            if '.git' in abs_path:
                continue
            f = None
            try:
                f = open(abs_path,'r')
                dt = f.read(20)
            except Exception as e:
                print('not file', e,abs_path)
            else:
                if "<!DOCTYPE html>".lower() in dt.lower() or "<html" in dt:
                    Files.append(abs_path)
                else:
                    print('doc type not find',abs_path)
            finally:
                if f:
                    f.close()

        # else:
main()
# hi = []
# for path,_, files in os.walk('.'):
#     for file in files:
#         abs_path = os.path.join(path,file)
#         if os.path.isfile(abs_path) and os.path.splitext(abs_path)[1] == '.hi':
#             hi.append(abs_path)