import os, re, base64, json, urllib.request, time

TOKEN = "c276c9d83a3406356e08c4902c129629"
DESKTOP = r"c:\Users\梁皓翔\Desktop\学习笔记"
POSTS = r"c:\Users\梁皓翔\Desktop\blog\source\_posts"
API = "https://gitee.com/api/v5/repos/jerry798/xcximg/contents/img"

# 从文章中提取所有图片文件名
refs = set()
for fn in os.listdir(POSTS):
    if not fn.endswith('.md'): continue
    with open(os.path.join(POSTS, fn), encoding='utf-8') as f:
        imgs = re.findall(r'gitee\.com/jerry798/xcximg/raw/master/img/([a-f0-9_\-]+\.(?:jpeg|jpg|png|gif|webp))', f.read())
        refs.update(imgs)
print(f"文章引用: {len(refs)} 张")

# 索引桌面所有图片
idx = {}
for r, d, fs in os.walk(DESKTOP):
    for f in fs:
        if f.lower().endswith(('.jpeg','.jpg','.png','.gif','.webp')):
            idx[f] = os.path.join(r, f)
print(f"本地图片: {len(idx)} 个")

# 需要上传的
to_upload = sorted([f for f in refs if f in idx])
missing_local = refs - set(idx.keys())
print(f"需上传: {len(to_upload)} 张")
if missing_local:
    print(f"本地缺失: {len(missing_local)} 张")

# 上传
ok, fail = 0, 0
for i, fn in enumerate(to_upload):
    fp = idx[fn]
    try:
        with open(fp, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        req = urllib.request.Request(f"{API}/{fn}",
            data=json.dumps({"access_token":TOKEN,"message":"up","content":b64}).encode(),
            headers={"Content-Type":"application/json;charset=UTF-8"}, method="POST")
        urllib.request.urlopen(req, timeout=60)
        print(f"[{i+1}/{len(to_upload)}] OK: {fn}")
        ok += 1
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8','ignore')
        if 'exist' in err.lower() or '存在' in err:
            print(f"[{i+1}/{len(to_upload)}] EXISTS: {fn}")
            ok += 1
        else:
            print(f"[{i+1}/{len(to_upload)}] FAIL HTTP{e.code}")
            fail += 1
    except Exception as e:
        print(f"[{i+1}/{len(to_upload)}] FAIL {e}")
        fail += 1
    time.sleep(0.3)

print(f"\nDone! OK:{ok} FAIL:{fail}")
