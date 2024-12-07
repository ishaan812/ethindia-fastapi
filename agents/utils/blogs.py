import http.client
import json


def addBlogPost(content: dict, mermaidstr: str):
    print("adding", content, mermaidstr)
    output = StoreToWalrus(mermaidstr)
    print(output)
    try:
        blobId = json.loads(output)["newlyCreated"]["blobObject"]["blobId"]
    except:
        blobId = json.loads(output)["alreadyCertified"]["blobId"]
    content["blobId"] = blobId
    with open("store/blogs.txt", "a") as f:
        f.write(str(content) + "\n")

def StoreToWalrus(mermaidString: str):
    conn = http.client.HTTPSConnection("publisher.walrus-testnet.walrus.space")
    payload = mermaidString
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded'
    }
    conn.request("PUT", "/v1/store", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))
    return data.decode("utf-8")


