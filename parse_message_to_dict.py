def parse_message_to_dict(message):
    # 메시지에서 대괄호 제거
    message = message.strip('[]')

    # 문자열을 ", "로 분리하여 키-값 쌍으로 나눕니다
    pairs = message.split(", ")

    # 딕셔너리에 키-값 쌍을 추가합니다
    result = {}
    for pair in pairs:
        key, value = pair.split('=', 1)  # 첫 번째 '=' 문자에서만 분리합니다.
        result[key] = value

    return result