# https://github.com/AlexHodgson/steamid-converter


import re

# 定义一些正则表达式的东西
STEAM_ID_REGEX = "^STEAM_"
STEAM_ID_3_REGEX = "^\[.*\]$"

# steamID64 都偏离这个值
ID64_BASE = 76561197960265728


def convert_steamID(steamID, target_format: str, as_int=False):
    """
    转换方法的包装器，允许您通过相同的函数调用不同的转换

    参数
    ----------
    steamID : int or str
        要转换的任何格式的 steamID

    target_format : str
        将 steamId 转换为的格式
        可能的值有：SteamID、SteamID3、SteamID64

    as_int : bool
        如果 SteamId64 作为 int 或字符串返回
        仅在 target_format = SteamId64 时使用
        Default = False


    Returns
    -------
    int or str
        steamID value

    """

    if target_format == 'SteamID':
        return to_steamID(steamID)

    elif target_format == 'SteamID3':
        return to_steamID3(steamID)

    elif target_format == 'SteamID64':
        return to_steamID64(steamID, as_int)

    else:
        raise ValueError("Incorrect target Steam ID format. Target_format must be one of: SteamID, SteamID3, SteamID64")


def to_steamID(steamID):
    """
    转换为 steamID

    每个 Steam 帐户都有一个唯一的 SteamID,
    用数字格式化为 x "STEAM_0:x:xxxxxxxx"

    参数
    ----------
    蒸汽 ID : int 或 str
        steamID3 或 steamID64 转换为 steamID

    Returns
    -------
    str
        steamID value

    """

    id_str = str(steamID)

    if re.search(STEAM_ID_REGEX, id_str):  # 已经是steamID
        return id_str

    elif re.search(STEAM_ID_3_REGEX, id_str):  # 如果传了steamID3

        id_split = id_str.split(":")  # 将字符串拆分为“Universe”、帐户类型和帐号
        account_id3 = int(id_split[2][:-1])  # 从 steamID3 的末尾删除 ]

        account_type = account_id3 % 2

        account_id = (account_id3 - account_type) // 2

    elif id_str.isnumeric():  # 通过了steamID64

        check_steamID64_length(id_str)  # 验证传入的id

        offset_id = int(id_str) - ID64_BASE

        # Get the account type and id
        account_type = offset_id % 2

        account_id = ((offset_id - account_type) // 2)

    return "STEAM_0:" + str(account_type) + ":" + str(account_id)


def to_steamID3(steamID):
    """
    转换成steamID3

    每个 steam 帐户都有一个 steamID3，
    将数字格式化为 x "[U:1:xxxxxxxx]"

    参数
    ----------
    steamID : int or str
        steamID 或 steamID64 转换为 steamID3

    Returns
    -------
    str
        steamID3 value

    """

    id_str = str(steamID)

    if re.search(STEAM_ID_3_REGEX, id_str):  # 已经是steamID3
        return id_str

    elif re.search(STEAM_ID_REGEX, id_str):  # 如果传递了 steamID

        id_split = id_str.split(":")  # 将字符串拆分为“Universe”、帐户类型和帐号

        account_type = int(id_split[1])  # 检查帐户类型
        account_id = int(id_split[2])  # 账号，添加到id3时需要加倍

        # 以steamID3格式一起加入
        return "[U:1:" + str(((account_id + account_type) * 2) - account_type) + "]"

    elif id_str.isnumeric():  # 通过了steamID64

        check_steamID64_length(id_str)  # 验证传入的id

        offset_id = int(id_str) - ID64_BASE

        # Get the account type and id
        account_type = offset_id % 2

        account_id = ((offset_id - account_type) // 2) + account_type

        # Join together in steamID3 format
        return "[U:1:" + str((account_id * 2) - account_type) + "]"

    else:
        raise ValueError(f"Unable to decode steamID: {steamID}")


def to_steamID64(steamID, as_int=False):
    """
    转换成steamID64

    steamID64 是一个 17 位数字，每个 steam 帐户都是唯一的

    Parameters
    ----------
    steamID : int or str
        steamID or steamID3 to convert to steamID64
    as_int : bool
        If the steamID64 is returned as an integer rather than string, Default = False

    Returns
    -------
    int or str
        steamID64 value

    """

    id_str = str(steamID)
    id_split = id_str.split(":")  # Split string into 'Universe', Account type, and Account number

    if id_str.isnumeric():  # Already a steamID64

        check_steamID64_length(id_str)  # Validate id passed in
        if as_int:
            return int(id_str)
        else:
            return id_str

    elif re.search(STEAM_ID_REGEX, id_str):  # If passed steamID

        account_type = int(id_split[1])  # Check for account type
        account_id = int(id_split[2])  # Account number, needs to be doubled when added to id64

    elif re.search(STEAM_ID_3_REGEX, id_str):  # If passed steamID3

        account_id3 = int(id_split[2][:-1])  # Remove ] from end of steamID3

        account_type = account_id3 % 2

        account_id = (account_id3 - account_type) // 2

    else:
        raise ValueError(f"Unable to decode steamID: {steamID}")

    id64 = ID64_BASE + (account_id * 2) + account_type

    # Check if returning as string or integer
    if as_int:
        return id64
    else:
        return str(id64)


def check_steamID64_length(id_str: str):
    """
    检查 steamID64 的长度是否正确，如果不正确则引发 ValueError。

    不是真的供你使用

    Parameters
    ----------
    id_str : str
        steamID64 to check length of

    """

    if len(id_str) != 17:
        raise ValueError(f"Incorrect length for steamID64: {id_str}")
