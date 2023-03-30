from apps import aliyundriver, lixianla

if __name__ == '__main__':
    try:
        aliyundriver
    except Exception as e:
        print(e)

    try:
        lixianla
    except Exception as e:
        print(e)
