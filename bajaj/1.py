import requests

url = 'http://127.0.0.1:8000/get-lab-tests'
files = {'file': open('test_images/BLR-0425-PA-0039192_E-PareshwarFinalBill_250427_1337@E.pdf_page_88.png', 'rb')}
response = requests.post(url, files=files)
print(response.json())

