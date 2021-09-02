def handler(response, context):
    if response and context:
        print(response, context, sep='\n')
    else:
        print('null')
