class AnnoworkCliException(Exception):
    """
    annoworkcliに関するException
    """


class CommandLineArgumentError(AnnoworkCliException):
    """コマンドライン引数が正しくない場合のエラー"""
