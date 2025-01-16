import requests

def main():
    response = requests.get("http://www.google.com/")
    print("Status code: ", response.status_code)
    print("Headers: ", response.headers)

if __name__ == "__main__":
    main()