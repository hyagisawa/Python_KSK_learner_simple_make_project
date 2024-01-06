import re
import shutil
from pathlib import Path
import json

# 紙面に残すアプリ ID
# コンテンツリスト内からデータ抽出
live_sim_list: list[str] = [
    "s1-19",
    "s1-20",
    "s1-45",
    "s1-46",
    "s1-47",
    "s2-3",
    "s2-17",
    "s2-50",
    "s2-51",
    "s3-12",
    "s3-13",
    "s3-21",
    "s3-22",
    "s3-26",
    "s3-27",
    "s3-35",
    "s3-36",
    "s3-37",
    "s4-9",
    "s4-16",
    "s4-25",
    "s4-26",
    "s4-27",
    "s4-40",
    "s4-41",
    "s4-44",
    "s4-47",
    "s4-48",
    "s4-49",
    "s4-60",
    "s4-61",
    "s4-62",
    "s4-64",
    "s4-65",
    "s4-67",
    "s4-68",
    "s5-6",
    "s5-8",
    "s5-9",
    "s5-11",
    "s5-12",
    "s5-13",
    "s5-14",
    "s5-15",
    "s5-17",
    "s5-41",
    "s5-43",
    "s5-45",
    "s5-46",
    "s5-47",
    "s5-50",
    "s5-51",
    "s6-4",
    "s6-5",
    "s6-6",
    "s6-7",
    "s6-10",
    "s6-11",
    "s6-19",
    "s6-20",
    "s6-21",
    "s6-22",
    "s6-30",
    "s6-33",
    "s6-35",
    "s6-36",
]


target_folder_name_pattern = r"KSK_R6_SANSU_\d_T|KSK_R6_SANSU_\d[AB]_T"

pattern_json: str = r"^[\s\S]*?({[\s\S]*?});"  # config ファイルから、JSON 部分を取得
path_to_me: Path = Path(__file__).resolve().parent  # スクリプトの設置されたバス
pattern_ID: str = r"^(KSK_R6_SANSU_\d_)T$|^(KSK_R6_SANSU_\d[AB]_)T$"  # 指導者用設定ファイルにマッチ

app_folder: Path = path_to_me.joinpath("apps")  # アプリフォルダ
pdf_folder: Path = path_to_me.joinpath("pdfs")  # PDF フォルダ
video_folder: Path = path_to_me.joinpath("videos")  # ビデオフォルダ
page_image_folder: Path = path_to_me.joinpath("pages/n")  # ページ画像
icon_image_folder: Path = Path(path_to_me).joinpath("icons")  # アイコン画像


def point_sim(s: str, l: list[str]) -> bool:
    """_summary_

    Args:
        s (str): リスト内から検索する文字列
        : (list[str]): 検索対象リスト

    Returns:
        bool: リスト内の文字列と一致したら True を戻す
    """
    f: bool = False

    for p in l:
        if s == p:
            f = True
            break

    return f


def file_backup(path: Path, mov: bool = False, ext: str = "") -> int:
    """_summary_

    Args:
        path (Path): バックアップ対象ファイルパス
        mov (bool, optional): 元の場所にファイルを残さずに移動 初期値=False
        ext (str, optional): ファイルの拡張子を変更する場合は引数に拡張子を入力 初期値=""（変更なし）

    Returns:
        int: バックアップ成功時 0 不成功の場合は -1 を戻す
    """
    # バックアップ対象ファイルが存在しない場合は処理中断
    if path.exists() == False:
        return -1

    # バックアップ先ディレクトリ Path を作成
    b: Path = path.parent.joinpath("_backup")

    # バックアップ先ディレクトリがなければ作成
    if b.exists() == False:
        b.mkdir()

    f: Path = Path("")

    # バックアップファイルの Path を作成
    # 拡張子の変更指定がる場合は変更する
    if ext != "":
        f = b.joinpath(f"{path.stem}.{ext}")
    else:
        f = b.joinpath(f"{path.name}")

    # ファイルのバックアップ（コピー or 移動）
    shutil.move(path, f) if mov == True else shutil.copy2(path, f)

    return 0


def folder_backup(path: Path, mov: bool = False) -> int:
    """_summary_

    Args:
        path (Path): バックアップ対象ディレクトリパス
        mov (bool, optional): 元の場所にディレクトリを残さず移動 初期値=False

    Returns:
        int: _description_
    """
    # バックアップ対象ファイルが存在しない場合は処理中断
    if path.exists() == False:
        return -1

    # バックアップ先ディレクトリ Path を作成
    b: Path = path.parent.joinpath("_backup")
    if b.exists() == False:
        b.mkdir()

    # バックアップ先の Path を作成
    f: Path = b.joinpath(path.name)

    # ディレクトリのバックアップ（コピー or 移動）
    shutil.move(path, f) if mov == True else shutil.copy2(path, f)

    return 0


def change_category(bookId: str, category_ch: str) -> str:
    """_summary_

    Args:
        bookId (str): bookID
        category_ch (str): カテゴリーキャラクタ 例）T:教師用 D:学習者用（シンプル） M:学習者用教材

    Returns:
        str: 変更後の bookID
    """
    prefixID: str = bookId[:-1]
    reslut: str = f"{prefixID}{category_ch}"
    return reslut


def remove_slide_resorce(pageInfos: list[dict]):
    """_summary_

    Args:
        pageInfos (list[dict]): _description_
    """
    for pg in pageInfos:
        slide_image = page_image_folder.joinpath(pg["filename"])
        if slide_image.exists() == True:
            file_backup(slide_image, True)  # スライド画像のバックアップ

        for cp in pg["clickPoint"]:
            resType: int = cp["resInfo"]["resType"]  # 遷移:4
            cpIcon: str = cp["cpIcon"]  # icon リソース
            resLinkType: int = cp["resInfo"]["resLink"]["type"]  # 別タブ（スライド）:5
            cpAlpha: int = cp["cpAlpha"]
            resMekuritype = cp["resInfo"]["resMekuri"]["type"]

            if resType == 4 and resLinkType == 5 and "thum_" in cpIcon:
                ico = icon_image_folder.joinpath(cpIcon)
                file_backup(ico, True)  # サムネイル画像のバックアップ

            if resType == 5 and cpAlpha == -1 and resMekuritype == 1:
                if None != re.search(r"^h\d.+\d.png", cpIcon):
                    ico = icon_image_folder.joinpath(cpIcon)
                    file_backup(ico, True)  # アイコン画像のバックアップ


def remove_source_cp(pageInfos: list[dict]) -> list[dict]:
    """_summary_

    Args:
        pageInfos (list[dict]): pageInfos list

    Returns:
        list[dict]: 不要 CP を除いたリストを戻す
    """

    n: list[dict] = []

    for pg in pageInfos:
        c: list[dict] = pg["clickPoint"]
        l: list[int] = []  # スライド遷移 cp のインデックスを入れるリスト

        for i, cp in enumerate(c):
            resType: int = cp["resInfo"]["resType"]  # 遷移:4
            resLinkType: int = cp["resInfo"]["resLink"]["type"]  # 別タブ（スライド）:5
            chapter: int = cp["resInfo"]["resLink"]["chapter"]  # チャプター番号
            appId: str = cp["resInfo"]["resLink"]["appId"]  # チャプター番号
            resAppId: str = cp["resInfo"]["resAppId"]  # アプリID ※ 自己評価
            resSrc: str = cp["resInfo"]["resSrc"]
            resLinkUrl: str = cp["resInfo"]["resLink"]["url"]  # チャプター番号
            cpIcon: str = cp["cpIcon"]  # アイコン設定
            cpColor: str = cp["cpColor"]
            cpAlpha: int = cp["cpAlpha"]

            # スライド遷移ボタンを捜索 あればリストに追加
            if resType == 4 and resLinkType == 5 and chapter >= 101 and chapter <= 599:
                l.append(i)

            # シミュレーションアプリ
            elif (
                resType == 4
                and resLinkType == 3
                and None != re.search(r"^s\d-\d{1,}$", appId)
            ):
                if point_sim(appId, live_sim_list) == False:
                    
                    # シミュレーションアプリのバックアップ
                    folder_backup(app_folder.joinpath(appId), True)
                    l.append(i)
                    

            # ズーム
            elif resType == 6 and resLinkType == 0:
                l.append(i)

            # 自己評価
            elif resType == 3 and resAppId == "SLF_ASS":
                # 自己評価アプリのバックアップ
                folder_backup(app_folder.joinpath(resAppId), True)
                l.append(i)

            # 動画
            elif resType == 1 and ".mp4" in resSrc:
                if "_manabi_" not in cpIcon:
                    # 動画のバックアップ
                    file_backup(video_folder.joinpath(resSrc), True)
                    l.append(i)

            # ワークシート PDFへ遷移
            elif resType == 4 and resLinkType == 4:
                if None != re.search(r"\.pdf$", resLinkUrl):
                    pdf_backup_path: Path = pdf_folder.joinpath(resLinkUrl[7:])
                    # ワークシート PDF のバックアップ
                    file_backup(pdf_backup_path, True)
                    l.append(i)

            # めくり紙
            elif resType == 5 and cpColor == "#80b3ff":
                l.append(i)

        # スライド遷移ボタンを削除 ※ ループ逆廻し
        for i in reversed(l):
            c.pop(i)

        pg["clickPoint"] = c
        n.append(pg)

    for j, pg in enumerate(n):
        for i, cp in enumerate(pg["clickPoint"]):
            resType: int = cp["resInfo"]["resType"]
            resLinkType: int = cp["resInfo"]["resLink"]["type"]
            url: int = cp["resInfo"]["resLink"]["url"]
            bookID: str = cp["resInfo"]["resLink"]["bookId"]
            resSrc: str = cp["resInfo"]["resSrc"]

            # 学びリンクの QR コード上のアイコン消去
            if "icon_manabi" in pg["clickPoint"][i]["cpIcon"]:
                pg["clickPoint"][i]["cpIcon"] = ""
                pg["clickPoint"][i]["cpAlpha"] = -1

            if resType == 4 and resLinkType == 4 and "./apps/" in url:
                app_: str = re.sub(r"\./apps/(Q\d{1,}-\d{1,})/index.html", "\\1", url)
                folder_backup(
                    app_folder.joinpath(app_),
                    True,
                )
                pg["clickPoint"][i]["resInfo"]["resLink"][
                    "url"
                ] = "https://www.kyoiku-shuppan.co.jp/m-link/img/manabi_top2.jpg"  # Dummy URL

            # 遷移先の bookId を修正
            if resType == 4 or resType == 5 or resType == 6:
                if None != re.search(pattern_ID, bookID):
                    pg["clickPoint"][i]["resInfo"]["resLink"][
                        "bookId"
                    ] = change_category(bookID, "D")

            if resType == 1 and ".mp4" in resSrc:
                file_backup(
                    video_folder.joinpath(pg["clickPoint"][i]["resInfo"]["resSrc"]),
                    True,
                )
                pg["clickPoint"][i]["resInfo"]["resType"] = 4
                pg["clickPoint"][i]["resInfo"]["resSrc"] = ""
                pg["clickPoint"][i]["resInfo"]["resLink"]["type"] = 4
                pg["clickPoint"][i]["resInfo"]["resLink"][
                    "url"
                ] = "https://www.kyoiku-shuppan.co.jp/materials/img/title.png"  # Dummy URL

        n[j] = pg

    return n


"""####################################################################################
#######################################################################################
main 関数
#######################################################################################
####################################################################################"""
if __name__ == "__main__":
    # if target_folder_name_pattern
    if None == re.search(target_folder_name_pattern, path_to_me.name):
        input("処理対象ではないようです。\n終了するには何かキーを押してください....")

    original_bookID: str = ""

    files: Path.glob = path_to_me.glob("./configs/ffl-chapter_*.js")

    for fl in files:
        chapter_num: int = int(re.sub(r"^.+_(\d{1,})-.+$", "\\1", fl.name))

        data: str = ""
        with open(fl, mode="r", encoding="utf_8") as f:
            data = f.read()

        json_data: str = re.sub(pattern_json, "\\1", data)  # JSON 部分の抽出

        j: dict = {}
        try:
            j = json.loads(json_data, strict=False)  # JSON 文字列を Ptyon 辞書型に変換

        except json.JSONDecodeError as e:
            print(fl.name)
            print(f"JSONデータのパースエラー: {e}")
            continue

        book_id: str = j["commonInfo"]["cmnBookId"]
        original_bookID = book_id

        if re.search(pattern_ID, book_id) is None:  # book ID が処理対象ではない場合は中断
            # print(f"処理対象外：{chapter_num}")
            continue

        kind: str = j["chapterInfo"]["name"]

        j["commonInfo"]["cmnBookId"] = change_category(book_id, "D")  # 学習者用の ID に変更

        pageInfos: list[dict] = j["chapterInfo"]["pageInfos"]

        if (
            kind == "紙面"
            or kind == "ワークシート"
            or kind == "学びの手引き"
            or kind == "つかい方・学び方"
            or kind == "ふりかえり"
        ):
            # 不要な cp 削除
            j["chapterInfo"]["pageInfos"] = remove_source_cp(pageInfos)
            file_backup(fl)
            with open(fl, mode="w", encoding="utf_8") as f:
                dump_Data: str = json.dumps(j, ensure_ascii=False)
                data: str = f"var chapter_{chapter_num}_Info = {dump_Data};"
                f.write(data)

        elif kind == "スライド":
            remove_slide_resorce(pageInfos)
            file_backup(fl, True)

    """################################################################################
    ###################################################################################
    ffl-book-config.js の bookId を変更
    ###################################################################################
    ################################################################################"""

    book_config: Path = path_to_me.joinpath("./configs/ffl-book-config.js")

    if book_config.exists() == True:
        data: str = ""
        with open(book_config, mode="r", encoding="utf_8") as f:
            data = f.read()

        json_data: str = re.sub(pattern_json, "\\1", data)  # JSON 部分の抽出
        j: dict = {}
        try:
            j = json.loads(json_data, strict=False)  # JSON 文字列を Ptyon 辞書型に変換

        except json.JSONDecodeError as e:
            print(f"JSONデータのパースエラー: {e}")

        book_id: str = j["bookInfo"]["bookId"]

        if re.search(pattern_ID, book_id) is None:  # book ID が処理対象ではない場合は中断
            print(f"処理対象外：{chapter_num}")

        else:
            book_title = re.sub(r"^指導者用(.+)$", "\\1", j["bookInfo"]["title"])
            j["bookInfo"]["bookId"] = change_category(j["bookInfo"]["bookId"], "D")
            j["linkInfo"]["bookId"] = change_category(j["bookInfo"]["bookId"], "D")
            j["bookInfo"]["title"] = f"学習者用{book_title}"

            file_backup(book_config)  # バックアップ
            with open(book_config, mode="w", encoding="utf_8") as f:
                dump_Data: str = json.dumps(j, ensure_ascii=False)
                data: str = f"var commonInfo = {dump_Data};"
                f.write(data)

    """################################################################################
    ###################################################################################
    fs_com_sidebar_config.js の bookId を変更
    ###################################################################################
    ################################################################################"""

    sidebar_config: Path = path_to_me.joinpath("./configs/fs_com_sidebar_config.js")

    if sidebar_config.exists() == True:
        data: str = ""
        with open(sidebar_config, mode="r", encoding="utf_8") as f:
            data = f.read()

        change_bookID: str = change_category(original_bookID, "D")
        s: str = re.sub(original_bookID, change_bookID, data)

        new_data: str = data.replace(original_bookID, change_bookID)

        file_backup(sidebar_config)

        with open(sidebar_config, mode="w", encoding="utf_8") as f:
            f.write(new_data)


input("終了するには、何かキーを押してください...")
