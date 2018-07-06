import requests,random,json
# import os
# os.chdir('spiders')
with open('proxy.json','r') as rf:
    data = json.loads(rf.read())

# proxy = random.choice(data)['https']
# print(proxy)

class RandomProxy:
    def process_request(self, request, spider):
        proxy = random.choice(data)['https']
        print(proxy)
        request.meta['proxy'] = '112.114.78.77:8118'

if __name__ == '__main__':
    pass



